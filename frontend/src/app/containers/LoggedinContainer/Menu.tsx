import * as React from "react";
import {
  Box,
  Avatar,
  Menu,
  ListItemIcon,
  Divider,
  IconButton,
  Tooltip,
  MenuItem,
} from "@mui/material";
import Logout from "@mui/icons-material/Logout";
import { upperCase, upperFirst } from "lodash";
import { Typography } from "@mui/material";
import { useNavigate } from "react-router-dom";
import BusinessIcon from "@mui/icons-material/Business";
import AccountCircleIcon from "@mui/icons-material/AccountCircle";
import SettingsIcon from "@mui/icons-material/Settings";

export default function AccountMenu({ data, profileData }) {
  const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null);
  const open = Boolean(anchorEl);
  const handleClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };
  const navigate = useNavigate();
  const handleClose = (to) => {
    if (to === "/") {
      localStorage.clear();
      sessionStorage.clear();
    }
    setAnchorEl(null);
    navigate(to);
  };

  return (
    <React.Fragment>
      <Box
        sx={{
          display: "flex",
          alignItems: "center",
          textAlign: "center",
          cursor: "pointer",
        }}
        onClick={handleClick}
      >
        <Tooltip title="Account settings">
          <Box
            display={"flex"}
            justifyContent={"center"}
            alignItems={"center"}
            gap={1}
          >
            <IconButton sx={{ p: 0 }}>
              {data?.profile_photo ? (
                <Avatar
                  alt={data?.name ?? "B"}
                  src={data?.profile_photo ?? ""}
                />
              ) : (
                <Avatar sx={{ width: 40, height: 40 }}>
                  {upperCase(profileData?.first_name).substring(0, 1)
                    ? upperCase(profileData?.first_name).substring(0, 1)
                    : "B"}
                </Avatar>
              )}
            </IconButton>
            <Box textAlign={"left"}>
              <Typography variant="body1" fontWeight={"700"}>
                {upperFirst(profileData?.first_name ?? "")}
              </Typography>
              <Typography variant="h6" sx={{ fontSize: "12px" }}>
                {profileData?.type ?? ""}
              </Typography>
            </Box>
          </Box>
        </Tooltip>
      </Box>
      <Menu
        anchorEl={anchorEl}
        id="account-menu"
        open={open}
        onClose={handleClose}
        onClick={handleClose}
        PaperProps={{
          elevation: 0,
          sx: {
            background: (theme) => theme.palette.common.white,
            overflow: "visible",
            filter: "drop-shadow(0px 2px 8px rgba(0,0,0,0.32))",
            mt: 1.5,
            "& .MuiAvatar-root": {
              width: 32,
              height: 32,
              ml: -0.5,
              mr: 1,
            },
            "&::before": {
              content: '""',
              display: "block",
              position: "absolute",
              top: 0,
              right: 14,
              width: 10,
              height: 10,
              bgcolor: "background.default",
              transform: "translateY(-50%) rotate(45deg)",
              zIndex: 0,
            },
          },
        }}
        transformOrigin={{ horizontal: "right", vertical: "top" }}
        anchorOrigin={{ horizontal: "right", vertical: "bottom" }}
      >
        <MenuItem onClick={() => handleClose("/dashboard/profile")}>
          <ListItemIcon>
            <AccountCircleIcon sx={{ mr: 2 }} />
          </ListItemIcon>
          Profile
        </MenuItem>
        <Divider />
        <MenuItem onClick={() => handleClose("/")}>
          <ListItemIcon>
            <Logout sx={{ mr: 2 }} />
          </ListItemIcon>
          Logout
        </MenuItem>
      </Menu>
    </React.Fragment>
  );
}
