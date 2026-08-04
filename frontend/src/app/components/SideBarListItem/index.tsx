import React, { memo, useState } from "react";
import ListItemButton from "@mui/material/ListItemButton";
import ListItemIcon from "@mui/material/ListItemIcon";
import ListItemText from "@mui/material/ListItemText";
import { useNavigate } from "react-router-dom";
import { Collapse, Icon, List, Tooltip } from "@mui/material";

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const Item = ({
  item,
  isSidebarOpen,
}: {
  item: any;
  isSidebarOpen: boolean;
}) => {
  const [isOpen, setIsOpen] = useState<boolean>(true);
  const navigate = useNavigate();
  const handleClick = (event: any, item) => {
    event.preventDefault();
    if (item?.children?.length) {
      setIsOpen(true);
    }
    navigate(`${item.href}/${item?.module_id ? item?.module_id : ""}`);
  };
  return (
    <React.Fragment>
      {isSidebarOpen ? (
        <ListItemButton
          autoFocus={window.location.href.includes(item.href)}
          key={item.name}
          onClick={(e) => handleClick(e, item)}
          sx={(theme) => ({
            ...(window.location.href.includes(item.href)
              ? {
                  bgcolor: theme.palette.primary.main,
                  color: "white",
                }
              : {
                  bgcolor: "transparent",
                  color: "text.primary",
                }),
            "&:hover": {
              bgcolor: (theme) => theme.palette.primary.main,
              color: "white",
              "& .MuiListItemIcon-root": {
                color: "inherit",
              },
            },
          })}
        >
          <ListItemIcon
            sx={() => ({
              ...(window.location.href.includes(item.href)
                ? {
                    color: "white",
                  }
                : {
                    bgcolor: "transparent",
                    color: "text.primary",
                  }),
            })}
          >
            <Icon component={item.icon}></Icon>
          </ListItemIcon>
          <ListItemText
            primary={item.name}
            sx={{ display: { xs: "none", sm: "block" } }}
          />
          {/* {item?.children?.length > 0 && (
            <>{isOpen ? <ExpandLess /> : <ExpandMore />}</>
          )} */}
        </ListItemButton>
      ) : (
        <Tooltip title={item.name}>
          <ListItemButton
            autoFocus={window.location.href.includes(item.href)}
            key={item.name}
            onClick={(e) => handleClick(e, item)}
          >
            <ListItemIcon>
              <Icon component={item.icon}></Icon>
            </ListItemIcon>
            <ListItemText
              primary={item.name}
              sx={{ display: { xs: "none", md: "block" } }}
            />
            {/* {item?.children?.length > 0 && (
              <>{isOpen ? <ExpandLess /> : <ExpandMore />}</>
            )} */}
          </ListItemButton>
        </Tooltip>
      )}
      {
        <Collapse
          in={item?.children?.length > 0 && isOpen}
          timeout="auto"
          unmountOnExit
          sx={{ ml: 0 }}
        >
          <List component="div" disablePadding>
            {item.children?.map((item1) => (
              <ListItemButton
                autoFocus={window.location.href.includes(item1.href)}
                key={item1.name}
                onClick={(e) => handleClick(e, item1)}
                sx={(theme) => ({
                  ...(window.location.href.includes(item1.href)
                    ? {
                        bgcolor: theme.palette.primary.main,
                        color: "white",
                      }
                    : {
                        bgcolor: "transparent",
                        color: "text.primary",
                      }),
                  "&:hover": {
                    bgcolor: (theme) => theme.palette.primary.main,
                    color: "white",
                    "& .MuiListItemIcon-root": {
                      color: "inherit",
                    },
                  },
                })}
              >
                <ListItemIcon
                  sx={() => ({
                    ...(window.location.href.includes(item1.href)
                      ? {
                          color: "white",
                          mr: -2,
                        }
                      : {
                          bgcolor: "transparent",
                          color: "text.primary",
                          mr: -2,
                        }),
                  })}
                >
                  <Icon component={item1.icon}></Icon>
                </ListItemIcon>
                <ListItemText primary={item1.name} />
              </ListItemButton>
            ))}
          </List>
        </Collapse>
      }
    </React.Fragment>
  );
};
export default memo(Item);
