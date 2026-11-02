import { useEffect, useRef, useState, type ReactNode } from 'react';

import { sendLocation } from '../api/drivers';
import { useSession } from '../hooks/useSession';
import type { LatLng } from '../lib/geo';
import { SEND_INTERVAL_MS, shouldSend, type Sent } from '../lib/locationSharing';
import { DriverLocationContext, type LocationStatus } from './driverLocationContext';

// A fix older than the send interval is not worth sending; a coarse one
// (network, not GPS) is enough to sort rides and saves the battery.
const WATCH_OPTIONS: PositionOptions = { enableHighAccuracy: false, maximumAge: SEND_INTERVAL_MS, timeout: 60_000 };
const SUPPORTED = typeof navigator !== 'undefined' && 'geolocation' in navigator;

type PhoneStatus = Exclude<LocationStatus, 'off'>;

/** While a driver is online, sends their position in the background, on
 *  every screen. Stops, and asks nothing more of the phone, once offline. */
export function DriverLocationProvider({ children }: { children: ReactNode }) {
  const { user } = useSession();
  const sharing = user?.role === 'driver' && user.isAvailable === true;
  // What the phone said last; 'waiting' again each time the driver goes online.
  const [status, setStatus] = useState<PhoneStatus>('waiting');
  const latest = useRef<LatLng | null>(null);
  const lastSent = useRef<Sent | null>(null);

  useEffect(() => {
    if (!sharing || !SUPPORTED) return;

    function trySend() {
      const position = latest.current;
      const now = Date.now();
      if (position === null || !shouldSend(position, now, lastSent.current)) return;
      lastSent.current = { position, at: now };
      // A failed send (2G cut, offline for the API) is simply retried at the next tick.
      sendLocation(position).catch(() => {
        lastSent.current = null;
      });
    }

    const watchId = navigator.geolocation.watchPosition(
      ({ coords }) => {
        latest.current = { lat: coords.latitude, lng: coords.longitude };
        setStatus('sharing');
        trySend();
      },
      (failure) => setStatus(failure.code === failure.PERMISSION_DENIED ? 'denied' : 'unavailable'),
      WATCH_OPTIONS,
    );
    // The phone reports only moves: a driver who waits still needs a fresh position.
    const tick = window.setInterval(trySend, SEND_INTERVAL_MS);
    return () => {
      navigator.geolocation.clearWatch(watchId);
      window.clearInterval(tick);
      latest.current = null;
      lastSent.current = null;
      setStatus('waiting');
    };
  }, [sharing]);

  const value: LocationStatus = !sharing ? 'off' : SUPPORTED ? status : 'unavailable';
  return <DriverLocationContext.Provider value={value}>{children}</DriverLocationContext.Provider>;
}
