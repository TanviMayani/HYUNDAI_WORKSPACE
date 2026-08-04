import * as React from "react";
import CssBaseline from "@mui/material/CssBaseline";
import Box from "@mui/material/Box";
import { useEffect } from "react";
import { Outlet } from "react-router-dom";
import { Stack, Paper } from "@mui/material";
import { useGetProfileQuery } from "../../redux/features/profile";
import AccountMenu from "./Menu";
import { setProfileData } from "../../redux/features/globalState";
import { useDispatch } from "react-redux";
import { useTokenCheckQuery } from "../../redux/features/commonApis";
import { useLocation } from "react-router-dom";

const profileInterceptor = (data) => {
  if (!data) {
    return;
  }
  return {
    email: data.email,
    group: data.group,
    last_name: data.last_name,
    id: data.id,
    language: data.language,
    last_login: data.last_login,
    member_since: data.member_since,
    name: data.name,
    profile_photo: data.profile_photo,
    timezone: data.timezone,
  };
};

export default function LoggedInContainer() {
  const { data: profileData } = useGetProfileQuery({});
  
  return (
    <Box sx={{ display: "flex" }}>
      <CssBaseline />
      <Box
        component="main"
        sx={{
          backgroundColor: (theme) =>
            theme.palette.mode === "light"
              ? theme.palette.grey[100]
              : theme.palette.grey[900],
          flexGrow: 1,
          height: "calc(100vh)",
          overflow: "auto",
          position: "relative",
          // marginTop: "52px",
        }}
      >
        <Box
          sx={{ position: "absolute", width: "100%", pr: 3, bgcolor: "white" }}
        >
          <Stack
            direction="row"
            spacing={2}
            justifyContent={"end"}
            sx={{ zIndex: 90000000 }}
          >
            <Paper
              elevation={0}
              sx={{
                background: (theme) => theme.palette.common.white,
                py: 1,
                px: 3,
                borderRadius: "4px",
              }}
            >
              <Box sx={{ flexGrow: 0 }}>
                <AccountMenu data={profileData} profileData={profileData} />
              </Box>
            </Paper>
          </Stack>
        </Box>
        <Outlet />
      </Box>
    </Box>
  );
}
