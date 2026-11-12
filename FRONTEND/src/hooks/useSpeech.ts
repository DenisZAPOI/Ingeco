import { useCallback, useEffect, useState } from 'react';

import { hasVoiceFor, sameLanguage } from '../lib/practicalGuides';

/** The speech synthesis of the browser, if it has one (Web Speech API, ADR 019). */
function speechSynthesisOrNull(): SpeechSynthesis | null {
  return typeof window !== 'undefined' && 'speechSynthesis' in window && 'SpeechSynthesisUtterance' in window
    ? window.speechSynthesis
    : null;
}

/** Reads a text aloud with a voice of the phone: no file to download, no
 *  service called (ADR 019). `available` is false when the phone has no voice
 *  for `lang`: the "Écouter" button is then hidden. Leaving the page stops it. */
export function useSpeech(lang: string) {
  const [synthesis] = useState(speechSynthesisOrNull);
  const [voices, setVoices] = useState<SpeechSynthesisVoice[]>(() => synthesis?.getVoices() ?? []);
  const [speaking, setSpeaking] = useState(false);

  // Many browsers list their voices only after a first "voiceschanged", which
  // may come between the first render and this effect: read them again here.
  useEffect(() => {
    if (!synthesis) return undefined;
    const update = () => setVoices(synthesis.getVoices());
    synthesis.addEventListener('voiceschanged', update);
    const late = window.setTimeout(update, 0);
    return () => {
      window.clearTimeout(late);
      synthesis.removeEventListener('voiceschanged', update);
    };
  }, [synthesis]);

  // Leaving the page stops the reading: it must not go on over another screen.
  useEffect(() => () => synthesis?.cancel(), [synthesis]);

  const speak = useCallback(
    (text: string) => {
      if (!synthesis) return;
      synthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = lang;
      const voice = voices.find((candidate) => sameLanguage(candidate.lang, lang));
      if (voice) utterance.voice = voice;
      utterance.onend = () => setSpeaking(false);
      utterance.onerror = () => setSpeaking(false);
      setSpeaking(true);
      synthesis.speak(utterance);
    },
    [synthesis, lang, voices],
  );

  const stop = useCallback(() => {
    synthesis?.cancel();
    setSpeaking(false);
  }, [synthesis]);

  return { available: synthesis !== null && hasVoiceFor(voices, lang), speaking, speak, stop };
}
