import React from "react";
import { useMatches, useNavigate } from "react-router-dom";

export const NotAuthorizedPage: React.FC = () => {
  const navigate = useNavigate();
  const matches = useMatches();

  // some crappy logic that allows us to redirect to /not-authorized/blah
  // and then match on blah to display custom error details
  // this is only for OIDC flows where we are pretty much limited to doing redirects
  let extraPath = "";

  if (matches && matches.length > 0) {
    const last = matches.slice(-1)[0];
    if (last && last.params) {
      if (last.params["*"]) extraPath = last.params["*"];
    }
  }

  return (
    <article className="prose max-w-none">
      {/* a set of redirect destinations from OIDC to show different messages */}
      {extraPath.includes("sub") && (
        <div className="alert alert-error">
          <span>
            No <span className="font-mono">sub</span> field in login claim set.
          </span>
        </div>
      )}
      {(extraPath.includes("email") || extraPath.includes("name")) && (
        <div className="alert alert-error">
          <span>
            No <span className="font-mono">email</span> or{" "}
            <span className="font-mono">name</span> field in login claim set.
          </span>
          <span>
            Email and name are vital parts of the functioning of the system so
            they must be provided by the upstream identity provider
          </span>
        </div>
      )}
      {extraPath.includes("flow") && (
        <div className="alert alert-error">
          <span>
            Login flow backend encountered an error so login process was
            aborted.
          </span>
          <span>Details of the error have been logged in the system logs.</span>
        </div>
      )}
      <p>You have logged in with an identity that is not authorized.</p>
      <p>
        <button
          className="btn btn-primary"
          onClick={async () => {
            navigate(`/login`);
          }}
        >
          Return to Login Page
        </button>
      </p>
    </article>
  );
};
