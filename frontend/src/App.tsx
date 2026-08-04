import "./App.css";
import { RouterProvider } from "react-router-dom";
import { router } from "./app/routes";
import { CssBaseline } from "@mui/material";
import { ThemeProvider } from "@emotion/react";
import { toastOptions } from "./app/constants";
import { Toaster } from "react-hot-toast";
import { store } from "./app/redux";
import { Provider } from "react-redux";
import { theme } from "./theme";
import { persistStore } from "redux-persist";
import { PersistGate } from "redux-persist/integration/react";
import PermissionsProvider from "./app/PermissionContext.jsx";
import { Suspense } from "react";
const persistor = persistStore(store);

function App() {
  return (
    <Provider store={store}>
      <PersistGate loading={null} persistor={persistor}>
        <PermissionsProvider>
          <div className="h-full w-full">
            <ThemeProvider theme={theme}>
              <CssBaseline />
              <Suspense fallback={<div>Loading...</div>}>
                <RouterProvider router={router} />
              </Suspense>
              <Toaster toastOptions={toastOptions} />
            </ThemeProvider>
          </div>
        </PermissionsProvider>
      </PersistGate>
    </Provider>
  );
}

export default App;
