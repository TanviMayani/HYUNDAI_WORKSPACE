import { List } from "@mui/material";
import { MainListItems } from "./listItems";

const SideBar = ({ isSidebarOpen }: { isSidebarOpen: boolean }) => {
  return (
    <List
      component="nav"
      sx={{
        display: "flex",
        flexDirection: { xs: "row", sm: "column" },
        my: 0,
        py: 2,
      }}
    >
      <MainListItems isSidebarOpen={isSidebarOpen} />
    </List>
  );
};

export default SideBar;
