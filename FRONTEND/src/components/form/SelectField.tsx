import { useEffect, useId, useRef, useState, type KeyboardEvent } from 'react';

import { movedIndex, TYPEAHEAD_RESET_MS, typeaheadIndex } from '../../lib/listbox';
import { CheckIcon, ChevronDownIcon } from '../ui/icons';
import type { Choice } from './ChoiceGroup';

type SelectFieldProps<Value extends string> = {
  label: string;
  choices: readonly Choice<Value>[];
  value: Value;
  onChange: (value: Value) => void;
};

/** A drop-down list drawn by us (the native one cannot follow the charter
 *  when open): a button that opens the options just below it. ARIA "listbox"
 *  pattern: arrows, Home, End, a typed letter, Enter or Space to choose,
 *  Escape to close; the focus goes back to the button. No library: about
 *  2 kB. For a filter, where tiles would take the whole screen. */
export function SelectField<Value extends string>({ label, choices, value, onChange }: SelectFieldProps<Value>) {
  const id = useId();
  const labelId = `${id}-label`;
  const listId = `${id}-list`;
  const optionId = (index: number) => `${id}-option-${index}`;

  const selectedIndex = Math.max(
    0,
    choices.findIndex((choice) => choice.value === value),
  );
  const [open, setOpen] = useState(false);
  const [active, setActive] = useState(selectedIndex);
  const buttonRef = useRef<HTMLButtonElement>(null);
  const listRef = useRef<HTMLUListElement>(null);
  const typed = useRef({ text: '', at: 0 });

  // Once open, the keyboard goes to the list, and the highlighted option stays in view.
  useEffect(() => {
    if (open) listRef.current?.focus();
  }, [open]);
  useEffect(() => {
    if (open) document.getElementById(`${id}-option-${active}`)?.scrollIntoView({ block: 'nearest' });
  }, [open, active, id]);

  function openList() {
    setActive(selectedIndex);
    setOpen(true);
  }

  function close(focusButton: boolean) {
    setOpen(false);
    if (focusButton) buttonRef.current?.focus();
  }

  function choose(index: number) {
    const choice = choices[index];
    if (choice && choice.value !== value) onChange(choice.value);
    close(true);
  }

  function handleButtonKey(event: KeyboardEvent<HTMLButtonElement>) {
    if (event.key === 'ArrowDown' || event.key === 'ArrowUp') {
      event.preventDefault();
      openList();
    }
  }

  function handleListKey(event: KeyboardEvent<HTMLUListElement>) {
    const moved = movedIndex(event.key, active, choices.length);
    if (moved !== null) {
      event.preventDefault();
      setActive(moved);
    } else if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      choose(active);
    } else if (event.key === 'Escape') {
      event.preventDefault();
      close(true);
    } else if (event.key === 'Tab') {
      close(false);
    } else if (event.key.length === 1 && !event.ctrlKey && !event.metaKey && !event.altKey) {
      const now = event.timeStamp;
      const text = now - typed.current.at < TYPEAHEAD_RESET_MS ? typed.current.text + event.key : event.key;
      typed.current = { text, at: now };
      const found = typeaheadIndex(
        choices.map((choice) => choice.label),
        text,
        active,
      );
      if (found !== null) setActive(found);
    }
  }

  return (
    <div className="field dropdown">
      <label id={labelId} htmlFor={id} className="field-label">
        {label}
      </label>
      <button
        ref={buttonRef}
        id={id}
        type="button"
        className="field-input dropdown-button"
        aria-haspopup="listbox"
        aria-expanded={open}
        aria-controls={listId}
        aria-labelledby={`${labelId} ${id}`}
        onClick={() => (open ? close(true) : openList())}
        onKeyDown={handleButtonKey}
      >
        <span className="dropdown-value">{choices[selectedIndex]?.label}</span>
        <ChevronDownIcon className="dropdown-chevron" />
      </button>
      {open && (
        <ul
          ref={listRef}
          id={listId}
          role="listbox"
          tabIndex={-1}
          className="dropdown-list"
          aria-labelledby={labelId}
          aria-activedescendant={optionId(active)}
          onKeyDown={handleListKey}
          // A tap or a click outside, or Tab: the list closes, nothing is chosen.
          onBlur={(event) => {
            if (!event.currentTarget.parentElement?.contains(event.relatedTarget)) setOpen(false);
          }}
        >
          {choices.map((choice, index) => (
            <li
              key={choice.value}
              id={optionId(index)}
              role="option"
              aria-selected={index === selectedIndex}
              className={index === active ? 'dropdown-option is-active' : 'dropdown-option'}
              onClick={() => choose(index)}
              onPointerMove={() => setActive(index)}
            >
              {choice.label}
              {index === selectedIndex && <CheckIcon className="dropdown-check" />}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
