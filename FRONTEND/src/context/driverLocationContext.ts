import { createContext } from 'react';

/** off: the driver is offline. waiting: asked the phone, no position yet.
 *  sharing: positions are sent. denied / unavailable: no position, the
 *  driver still sees the rides of the whole zone. */
export type LocationStatus = 'off' | 'waiting' | 'sharing' | 'denied' | 'unavailable';

export const DriverLocationContext = createContext<LocationStatus>('off');
