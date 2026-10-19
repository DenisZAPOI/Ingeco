import { useCallback } from 'react';

import { activate, login, register, type ActivateData, type LoginData, type RegisterData } from '../api/auth';
import { updateProfile, type ProfileChanges } from '../api/users';
import { useSession } from './useSession';
import { useSubmit } from './useSubmit';

// Each form opens (or updates) the session with the account the API returns.

export function useLogin() {
  const { setUser } = useSession();
  return useSubmit(useCallback((data: LoginData) => login(data).then(keep(setUser)), [setUser]));
}

export function useRegister() {
  const { setUser } = useSession();
  return useSubmit(useCallback((data: RegisterData) => register(data).then(keep(setUser)), [setUser]));
}

export function useActivate() {
  const { setUser } = useSession();
  return useSubmit(useCallback((data: ActivateData) => activate(data).then(keep(setUser)), [setUser]));
}

export function useUpdateProfile() {
  const { setUser } = useSession();
  return useSubmit(useCallback((changes: ProfileChanges) => updateProfile(changes).then(keep(setUser)), [setUser]));
}

function keep<T>(setUser: (user: T) => void) {
  return (user: T): T => {
    setUser(user);
    return user;
  };
}
