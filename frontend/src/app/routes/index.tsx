import { Navigate, Outlet, createBrowserRouter } from "react-router-dom";
import StaticContainer from "../containers/StaticContainer";
import LoginForm from "../pages/login";
import RegisterForm from "../pages/register";
import ResetPasswordForm from "../pages/resetPassword";
import ForgotPasswordForm from "../pages/forgetPassword";
import LoggedInContainer from "../containers/LoggedinContainer";
import MyJobsPage from "../pages/myJobs";
import ViewJobs from "../pages/ViewJobs";
import NotAllowed from "../pages/not-allowed";
import ProtectedRoute from "./auth/ProtectedRoute";
import RestrictedRoute from "./auth/RestrictedRoute";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <Navigate to={"/login"} />,
  },
  {
    path: "login",
    element: (
      <StaticContainer>
        <LoginForm />
      </StaticContainer>
    ),
  },
  {
    path: "forgot-password",
    element: (
      <StaticContainer>
        <ForgotPasswordForm />
      </StaticContainer>
    ),
  },
  {
    path: "reset-password",
    element: (
      <StaticContainer>
        <ResetPasswordForm />
      </StaticContainer>
    ),
  },
  {
    path: "register",
    element: (
      <StaticContainer>
        <RegisterForm />
      </StaticContainer>
    ),
  },

  {
    path: "dashboard",
    element: <RestrictedRoute element={<LoggedInContainer />} />,
    children: [
      {
        path: "my-jobs",
        element: <Outlet />,
        children: [
          {
            index: true,
            element: <ViewJobs />,
          },
          {
            path: ":viewId",
            element: <ViewJobs />,
          },
        ],
      },

      {
        path: "jobs/:id",
        element: (
          <ProtectedRoute element={<MyJobsPage />} moduleName="extract" />
        ),
      },

      {
        path: "not-allowed",
        element: <NotAllowed />,
      },
    ],
  },
]);
