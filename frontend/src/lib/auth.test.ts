import { describe, it, expect, beforeEach, vi } from "vitest";
import { checkCredentials, isAuthenticated, signIn, signOut } from "./auth";

describe("checkCredentials", () => {
  it("accepts valid credentials", () => {
    expect(checkCredentials("user", "password")).toBe(true);
  });

  it("rejects wrong username", () => {
    expect(checkCredentials("admin", "password")).toBe(false);
  });

  it("rejects wrong password", () => {
    expect(checkCredentials("user", "wrong")).toBe(false);
  });

  it("rejects empty credentials", () => {
    expect(checkCredentials("", "")).toBe(false);
  });
});

describe("session", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it("is not authenticated by default", () => {
    expect(isAuthenticated()).toBe(false);
  });

  it("is authenticated after signIn", () => {
    signIn();
    expect(isAuthenticated()).toBe(true);
  });

  it("is not authenticated after signOut", () => {
    signIn();
    signOut();
    expect(isAuthenticated()).toBe(false);
  });
});
