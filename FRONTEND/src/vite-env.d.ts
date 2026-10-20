// The VITE_ variables of .env, typed: without this they would be `any`.
interface ImportMetaEnv {
  readonly VITE_API_URL?: string;
  readonly VITE_CALL_CENTER_PHONE?: string;
}
