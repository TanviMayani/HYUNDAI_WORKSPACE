// src/app/PermissionsContext.js
import React, { createContext, useState, useEffect } from "react";
import { useSelector } from "react-redux";

export const PermissionsContext = createContext();

const PermissionsProvider = ({ children }) => {
  const permission = useSelector(
    (state) => state?.globalState?.profileData?.permission
  );
  const [permissions, setPermissions] = useState([]);

  useEffect(() => {
    setPermissions(permission);
  }, [permission]);

  return (
    <PermissionsContext.Provider value={permissions}>
      {children}
    </PermissionsContext.Provider>
  );
};

export default PermissionsProvider;
