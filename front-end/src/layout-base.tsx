import React, { PropsWithChildren } from "react";
import { Outlet } from "react-router-dom";
import { useLoggedInUser } from "./providers/logged-in-user-provider";

export const LayoutBase: React.FC<PropsWithChildren> = () => {
  const user = useLoggedInUser();

  return (
    <>
      <nav className="navbar navbar-dark bg-dark">
        <div className="container-fluid">
          <a className="navbar-brand">GA4GH Passport Tester</a>
          {user && (
            <>
              <li className="nav-item active">
                <a className="nav-link" href="#">
                  Home <span className="sr-only">(current)</span>
                </a>
              </li>
              <span className="navbar-text">
                Logged in as {user.displayName}
              </span>
              <form className="d-flex" action="/logout" method="POST">
                <button className="btn btn-outline-success" type="submit">
                  Logout
                </button>
              </form>
            </>
          )}
        </div>
      </nav>

      <div className="container pt-3">
        <Outlet />
      </div>
    </>
  );
};
