import { useId, useState } from 'react';

import type { Ride } from '../../api/rides';
import { useRateRide } from '../../hooks/useRides';
import { RATING_COMMENT_MAX_LENGTH, SCORES } from '../../lib/ride';
import { Form } from '../form/Form';
import { StarIcon } from '../ui/icons';

type RatingFormProps = {
  ride: Ride;
  onRated: (ride: Ride) => void;
};

const NO_SCORE = 'Choisissez une note, de 1 à 5 étoiles.';

/** Five large stars and an optional comment, at the end of the trip. */
export function RatingForm({ ride, onRated }: RatingFormProps) {
  const [score, setScore] = useState<number | null>(null);
  const [comment, setComment] = useState('');
  const [missingScore, setMissingScore] = useState(false);
  const rating = useRateRide(ride.id);
  const name = useId();
  const commentId = `${name}-comment`;
  const commentError = rating.errors.comment;

  async function send() {
    if (score === null) {
      setMissingScore(true);
      return;
    }
    const rated = await rating.submit({ score, comment: comment.trim() || null });
    if (rated) onRated(rated);
  }

  return (
    <Form
      onSubmit={send}
      submitLabel="Envoyer ma note"
      submitting={rating.submitting}
      error={missingScore && score === null ? NO_SCORE : rating.error}
    >
      <fieldset className="field rating-stars">
        <legend className="field-label">Comment s'est passé votre trajet ?</legend>
        <div className="rating-stars-row">
          {SCORES.map((value) => (
            <label key={value} className="rating-star">
              <input
                type="radio"
                name={name}
                value={value}
                checked={score === value}
                onChange={() => setScore(value)}
                className="visually-hidden"
              />
              <StarIcon filled={score !== null && value <= score} />
              <span className="visually-hidden">{value === 1 ? '1 étoile' : `${value} étoiles`} sur 5</span>
            </label>
          ))}
        </div>
        <p className="field-hint">1 étoile : très mauvais. 5 étoiles : très bien.</p>
      </fieldset>
      <div className="field">
        <label htmlFor={commentId} className="field-label">
          Un commentaire ? (facultatif)
        </label>
        <textarea
          id={commentId}
          className="field-input field-textarea"
          value={comment}
          onChange={(event) => setComment(event.target.value)}
          maxLength={RATING_COMMENT_MAX_LENGTH}
          aria-invalid={commentError ? true : undefined}
          aria-describedby={commentError ? `${commentId}-error` : undefined}
        />
        {commentError && (
          <p id={`${commentId}-error`} className="field-error">
            {commentError}
          </p>
        )}
      </div>
    </Form>
  );
}

/** A rating already given. */
export function RatingSummary({ score, comment }: { score: number; comment: string | null }) {
  return (
    <div className="panel">
      <p className="rating-stars-row" role="img" aria-label={`Votre note : ${score} sur 5`}>
        {SCORES.map((value) => (
          <StarIcon key={value} className="rating-star-shown" filled={value <= score} />
        ))}
      </p>
      {comment && <p className="rating-comment">« {comment} »</p>}
      <p className="note">Merci pour votre avis.</p>
    </div>
  );
}
