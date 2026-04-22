"use client";

import { useEffect, useState } from "react";
import { isAuthenticated, signOut } from "@/lib/auth";
import { SignInPage } from "@/components/SignInPage";
import { KanbanBoard } from "@/components/KanbanBoard";

export const App = () => {
  const [authed, setAuthed] = useState(false);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    setAuthed(isAuthenticated());
    setReady(true);
  }, []);

  if (!ready) return null;

  if (!authed) {
    return <SignInPage onSignIn={() => setAuthed(true)} />;
  }

  return (
    <KanbanBoard
      onLogout={() => {
        signOut();
        setAuthed(false);
      }}
    />
  );
};
