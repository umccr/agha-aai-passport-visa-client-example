import React from "react";
import {
  createBrowserRouter,
  createRoutesFromElements,
  Navigate,
  Outlet,
  Route,
  RouterProvider,
  useLocation,
} from "react-router-dom";
import { useLoggedInUser } from "./providers/logged-in-user-provider";
import { NotAuthorizedPage } from "./pages/not-authorized-page";
import { LoginPage } from "./pages/login-page";
import { LayoutBase } from "./layout-base";
import { WorkPage } from "./pages/work-page";

/**
 * Create the complete set of routes for the application.
 */
export function MainRouter() {
  // router for our "catch-all"
  const NoMatch = () => {
    let location = useLocation();

    return (
      <div className="alert alert-danger" role="alert">
        No React router match for <code>{location.pathname}</code>
      </div>
    );
  };

  // router that can wrap protected (must be logged in) sections
  const ProtectedRoute: React.FC<{ redirectPath: string }> = ({
    redirectPath,
  }) => {
    const userObject = useLoggedInUser();

    if (!userObject) {
      return <Navigate to={redirectPath} replace />;
    }

    return <Outlet />;
  };

  const router = createBrowserRouter(
    createRoutesFromElements(
      <Route element={<LayoutBase />}>
        {/* the following 'public' routes need to come first so that they will match before
            the more generic / route */}
        <Route path={`/login`} element={<LoginPage />} />

        {/* these 'public' routes are used by the OIDC flow to redirect if there is some
             reason the idP login works but we don't want to allow them in */}
        <Route path={`/not-authorized`} element={<NotAuthorizedPage />}>
          {/* some extra specific routes can give extra information to clarify the reason */}
          <Route path="*" element={<NotAuthorizedPage />} />
        </Route>

        {/* a protected hierarchy of routes - user must be logged in */}
        <Route path={`/`} element={<ProtectedRoute redirectPath="/login" />}>
          {/* our default 'home' is the releases page */}
          <Route index element={<Navigate to={"work"} />} />

          <Route path={`work`} element={<WorkPage />}></Route>
        </Route>

        <Route path="*" element={<NoMatch />} />
      </Route>,
    ),
  );

  return <RouterProvider router={router} />;
}
