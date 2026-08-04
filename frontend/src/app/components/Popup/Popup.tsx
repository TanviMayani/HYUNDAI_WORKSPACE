// ReusableDialog.js
import { Dialog, Box, Typography } from "@mui/material";
import ClearIcon from "@mui/icons-material/Clear";

const Popup = ({ open, onClose, children }) => {
  return (
    <>
      <Dialog fullWidth maxWidth={"md"} open={open} onClose={onClose}>
        <Box
          display={"flex"}
          justifyContent={"space-between"}
          px={3}
          py={2}
          onClick={onClose}
          borderBottom={"2px solid #e3e3e3"}
        >
          <Typography fontWeight={600}>Samples</Typography>
          <ClearIcon />
        </Box>
        <Box p={2}>{children}</Box>
      </Dialog>
    </>
  );
};

export default Popup;
