import { useEffect, useState } from "react";
import { useSelector } from "react-redux";
import { Navigate } from "react-router-dom";

export const AdminRoute = ({ element }) => {
  const type = useSelector((state) => state?.globalState?.profileData?.type);
  const [isLoading, setIsLoading] = useState(true);
  useEffect(() => {
    if (type !== undefined) {
      setIsLoading(false);
    }
  }, [type]);
  if (isLoading) {
    return "";
  }
  if (type !== undefined && type === "ADMIN") {
    return element;
  }
  if (type !== undefined && type !== "ADMIN") {
    return <Navigate to="/dashboard/not-allowed" />;
  }
};

export default AdminRoute;
