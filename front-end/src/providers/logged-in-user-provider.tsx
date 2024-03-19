import React from "react";
import { createCtx } from "./create-ctx";
import { useCookies } from "react-cookie";

export type LoggedInUser = {
  subjectIdentifier: string;
  email: string;
  displayName: string;
};

type Props = {
  children: React.ReactNode;
};

const LOGGED_IN_SUBJECT_IDENTIFIER_COOKIE_NAME = "logged_in_sub";
const LOGGED_IN_EMAIL_COOKIE_NAME = "logged_in_name";
const LOGGED_IN_DISPLAY_NAME_COOKIE_NAME = "logged_in_email";

/**
 * The logged-in user provider is a context that tracks the logged-in user via
 * cookies.
 *
 * @param props
 * @constructor
 */
export const LoggedInUserProvider: React.FC<Props> = (props: Props) => {
  const [cookies] = useCookies<any>([
    LOGGED_IN_SUBJECT_IDENTIFIER_COOKIE_NAME,
    LOGGED_IN_EMAIL_COOKIE_NAME,
    LOGGED_IN_DISPLAY_NAME_COOKIE_NAME,
  ]);

  const subjectIdentifier = cookies[LOGGED_IN_SUBJECT_IDENTIFIER_COOKIE_NAME];
  const email = cookies[LOGGED_IN_EMAIL_COOKIE_NAME];
  const displayName = cookies[LOGGED_IN_DISPLAY_NAME_COOKIE_NAME];

  const val =
    subjectIdentifier && email && displayName
      ? {
          subjectIdentifier: subjectIdentifier,
          email: email,
          displayName: displayName,
        }
      : null;

  return <CtxProvider value={val}>{props.children}</CtxProvider>;
};

export const [useLoggedInUser, CtxProvider] = createCtx<LoggedInUser | null>();
