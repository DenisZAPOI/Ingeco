// The only real-time connection of the project (Socket.IO, ADR 014), as
// client.ts is the only fetch. A screen follows what it shows (a ride, the
// offers): the connection opens with the first one and closes with the last,
// so it costs nothing elsewhere on a weak network. The library is loaded on
// demand, never on the first visit.
//
// The events are signals: the screen reads again over HTTP what changed, so
// what each person may see stays decided by the API. An event sent during a
// network cut is lost: the screen also reads again at every (re)connection.
//
// Not described by the OpenAPI document (it only knows HTTP routes): the
// messages below follow docs/contrat-api.md, part 5.

import type { Socket } from 'socket.io-client';

import { apiUrl, ensureSession, renewSession } from './client';

const RIDE_UPDATED = 'ride:updated';
const OFFERS_CHANGED = 'offers:changed';

type RideUpdate = { rideId: number; status: string };
type SubscriptionAck = { accepted: boolean };

type Subscription = {
  followEvent: string;
  unfollowEvent: string;
  message: { rideId: number } | Record<string, never>;
  changeEvent: string;
  concernsMe: (payload: unknown) => boolean;
  onChange: () => void;
};

const subscriptions = new Set<Subscription>();
// Null once given up: no session, or refused even after a renewal.
let connection: Promise<Socket | null> | null = null;

/** Calls `onChange` when the ride changes, and at every (re)connection. Returns the unfollow. */
export function followRide(rideId: number, onChange: () => void): () => void {
  return subscribe({
    followEvent: 'ride:follow',
    unfollowEvent: 'ride:unfollow',
    message: { rideId },
    changeEvent: RIDE_UPDATED,
    concernsMe: (payload) => isRideUpdate(payload) && payload.rideId === rideId,
    onChange,
  });
}

/** Calls `onChange` when a ride enters or leaves the drivers' offers, and at every (re)connection. */
export function followOffers(onChange: () => void): () => void {
  return subscribe({
    followEvent: 'offers:follow',
    unfollowEvent: 'offers:unfollow',
    message: {},
    changeEvent: OFFERS_CHANGED,
    concernsMe: () => true,
    onChange,
  });
}

function subscribe(subscription: Subscription): () => void {
  subscriptions.add(subscription);
  connection ??= open();
  void connection.then((socket) => {
    // Still wanted, and already connected: otherwise the 'connect' handler joins it.
    if (socket?.connected && subscriptions.has(subscription)) join(socket, subscription);
  });

  return () => {
    subscriptions.delete(subscription);
    void connection?.then((socket) => {
      if (socket === null) return;
      if (!isStillFollowed(subscription)) socket.emit(subscription.unfollowEvent, subscription.message);
      if (subscriptions.size === 0) close(socket);
    });
  };
}

async function open(): Promise<Socket | null> {
  if (!(await ensureSession())) {
    // Nobody logged in: the next screen that follows something tries again.
    connection = null;
    return null;
  }
  const { io } = await import('socket.io-client');
  // withCredentials: the session cookies go with the connection, as with fetch.
  const socket = io(apiUrl(''), { withCredentials: true });

  let renewedAfterRefusal = false;
  socket.on('connect', () => {
    renewedAfterRefusal = false;
    // A new connection is in no room: every screen subscribes again.
    subscriptions.forEach((subscription) => join(socket, subscription));
  });
  socket.on('connect_error', () => {
    // Still active: a network trouble, Socket.IO tries again by itself.
    if (socket.active) return;
    // Refused by the API: the 15-minute token is over. Renewed once; refused
    // again, the screens keep their "Actualiser" button.
    if (renewedAfterRefusal) return;
    renewedAfterRefusal = true;
    void renewSession().then((renewed) => {
      if (renewed) socket.connect();
    });
  });

  socket.on(RIDE_UPDATED, (payload: unknown) => notify(RIDE_UPDATED, payload));
  socket.on(OFFERS_CHANGED, () => notify(OFFERS_CHANGED, null));
  return socket;
}

function close(socket: Socket): void {
  socket.disconnect();
  connection = null;
}

/** Subscribes on the server; once accepted, the screen reads again what it may have missed. */
function join(socket: Socket, subscription: Subscription): void {
  socket.emit(subscription.followEvent, subscription.message, (ack: SubscriptionAck) => {
    if (ack.accepted && subscriptions.has(subscription)) subscription.onChange();
  });
}

function notify(event: string, payload: unknown): void {
  subscriptions.forEach((subscription) => {
    if (subscription.changeEvent === event && subscription.concernsMe(payload)) subscription.onChange();
  });
}

/** Another screen still follows the same thing: leaving the room would cut it off too. */
function isStillFollowed(left: Subscription): boolean {
  return [...subscriptions].some(
    (other) => other.followEvent === left.followEvent && sameMessage(other.message, left.message),
  );
}

function sameMessage(first: Subscription['message'], second: Subscription['message']): boolean {
  return JSON.stringify(first) === JSON.stringify(second);
}

function isRideUpdate(payload: unknown): payload is RideUpdate {
  return typeof payload === 'object' && payload !== null && 'rideId' in payload;
}
