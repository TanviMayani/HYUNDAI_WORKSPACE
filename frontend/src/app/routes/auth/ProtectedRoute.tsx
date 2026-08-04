import React, { useEffect, useState } from "react";
import { useSelector } from "react-redux";
import { Navigate } from "react-router-dom";

interface Permission {
  module_name: string;
  read: boolean;
}

interface ProtectedRouteProps {
  element: React.ReactNode;
  moduleName: string;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  element,
  moduleName,
}) => {
  const permissions = useSelector(
    (state) => state.globalState.profileData?.permission
  ) as Permission[] | undefined;
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [hasAccess, setHasAccess] = useState<boolean>(false);

  useEffect(() => {
    if (permissions) {
      const hasPermission = permissions.find(
        (perm) => perm.module_name === moduleName
      );
      setHasAccess(hasPermission?.read || false);
    }
    setIsLoading(false);
  }, [permissions, moduleName]);

  if (isLoading) {
    return <div>Loading...</div>;
  }

  if (hasAccess) {
    return <>{element}</>;
  }

  return <Navigate to="/dashboard/not-allowed" />;
};

export default ProtectedRoute;
