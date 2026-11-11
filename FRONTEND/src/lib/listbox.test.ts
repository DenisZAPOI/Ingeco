import { describe, expect, it } from 'vitest';

import { movedIndex, typeaheadIndex } from './listbox';

const COMMUNES = ['Toutes les communes', 'Cayenne', 'Matoury', 'Rémire-Montjoly'];

describe('movedIndex', () => {
  it('moves down and up, and stops at both ends', () => {
    expect(movedIndex('ArrowDown', 0, 4)).toBe(1);
    expect(movedIndex('ArrowDown', 3, 4)).toBe(3);
    expect(movedIndex('ArrowUp', 2, 4)).toBe(1);
    expect(movedIndex('ArrowUp', 0, 4)).toBe(0);
  });

  it('goes to the first and last option', () => {
    expect(movedIndex('Home', 2, 4)).toBe(0);
    expect(movedIndex('End', 0, 4)).toBe(3);
  });

  it('ignores other keys and empty lists', () => {
    expect(movedIndex('a', 1, 4)).toBeNull();
    expect(movedIndex('ArrowDown', 0, 0)).toBeNull();
  });
});

describe('typeaheadIndex', () => {
  it('finds a label by its first letters, without accents or capitals', () => {
    expect(typeaheadIndex(COMMUNES, 'm', 0)).toBe(2);
    expect(typeaheadIndex(COMMUNES, 're', 0)).toBe(3);
    expect(typeaheadIndex(COMMUNES, 'RÉM', 0)).toBe(3);
  });

  it('goes on to the next option with the same letter', () => {
    const labels = ['Cayenne', 'Cacao', 'Matoury'];
    expect(typeaheadIndex(labels, 'c', 0)).toBe(1);
    expect(typeaheadIndex(labels, 'c', 1)).toBe(0);
  });

  it('stays on the current option while several letters still match it', () => {
    expect(typeaheadIndex(COMMUNES, 'ca', 1)).toBe(1);
  });

  it('returns null when nothing matches', () => {
    expect(typeaheadIndex(COMMUNES, 'z', 0)).toBeNull();
    expect(typeaheadIndex(COMMUNES, '', 0)).toBeNull();
  });
});
