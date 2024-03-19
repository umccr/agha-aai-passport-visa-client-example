export const LoginPage: React.FC = () => {
  return (
    <>
      <p className="lead">
        To enter the environment we need to do a "Login Flow" - concerned with
        establishing your identity with the workspace/session.{" "}
        <strong>This flow is not a GA4GH Passport flow</strong>.
      </p>
      <div className="vstack gap-3">
        <p>
          The result of the login flow is just that some sort of persistent
          "session" is established with the front-end code. For this
          demonstrator, we have added two debug login bypasses - that just
          establish the session but do not need to do an actual flow.
        </p>
        <form
          action="/api/login-bypass-1"
          method="POST"
          id="loginBypass1TriggerForm"
        >
          <button className="btn btn-primary" type="submit">
            Bypass Log In Test User 1
          </button>
        </form>
        <form
          action="/api/login-bypass-2"
          method="POST"
          id="loginBypass2TriggerForm"
        >
          <button className="btn btn-primary" type="submit">
            Bypass Log In Test User 2
          </button>
        </form>
        <hr />
        <p>
          The code to perform a real OIDC flow is present in the back-end server
          - but requires private configuration of secrets. It is disabled out of
          the box. We may write instructions for this - but honestly - this is
          just regular OIDC - it is not actually important conceptually to
          demonstrate GA4GH passports or visas.
        </p>
        <form action="/login" method="POST" id="loginTriggerForm">
          <button className="btn btn-primary" type="submit" disabled={true}>
            Log In
          </button>
        </form>
      </div>
    </>
  );
};
