const VALID_USERNAME = "user";
const VALID_PASSWORD = "password";
const SESSION_KEY = "kanban_auth";

export function checkCredentials(username: string, password: string): boolean {
  return username === VALID_USERNAME && password === VALID_PASSWORD;
}

export function isAuthenticated(): boolean {
  if (typeof window === "undefined") return false;
  return localStorage.getItem(SESSION_KEY) === "1";
}

export function signIn(): void {
  localStorage.setItem(SESSION_KEY, "1");
}

export function signOut(): void {
  localStorage.removeItem(SESSION_KEY);
}
