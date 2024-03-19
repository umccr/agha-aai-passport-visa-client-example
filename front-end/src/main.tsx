import React from "react";
import ReactDOM from "react-dom/client";
import { CookiesProvider } from "react-cookie";
import { LoggedInUserProvider } from "./providers/logged-in-user-provider";
import { MainRouter } from "./main-router";
import { QueryClient, QueryClientProvider } from "react-query";

const queryClient = new QueryClient();

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <CookiesProvider>
      <QueryClientProvider client={queryClient}>
        <LoggedInUserProvider>
          <MainRouter />
        </LoggedInUserProvider>
      </QueryClientProvider>
    </CookiesProvider>
  </React.StrictMode>,
);
