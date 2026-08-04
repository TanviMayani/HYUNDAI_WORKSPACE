import { Box } from "@mui/material";
import RouteBreadcrumb from "../Breadcrumbs";

const TopPageHeader = () => {
  return (
    <Box sx={{ my: 2, px: 3 }}>
      <Box mt={8}>
        <RouteBreadcrumb />
      </Box>
    </Box>
  );
};
export default TopPageHeader;
