import { Navigate } from "react-router-dom";

const RestrictedRoute = ({ element }) => {
  const isToken = sessionStorage.getItem("token");
  if (isToken) {
    return element;
  }

  return <Navigate to={"/login"} />;
};

export default RestrictedRoute;
