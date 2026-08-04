// ReusableDialog.js
import { Dialog, DialogTitle, Box, Button } from "@mui/material";

const ConfirmPopup = ({
  open,
  onClose,
  onConfirm,
  title,
  confirmText = "Delete",
  cancelText = "Cancel",
}) => {
  return (
    <Dialog
      open={open}
      onClose={onClose}
      aria-labelledby="alert-dialog-title"
      aria-describedby="alert-dialog-description"
    >
      <DialogTitle id="alert-dialog-title">{title}</DialogTitle>
      <Box display={"flex"} justifyContent={"center"} mb={2}>
        <Button onClick={onClose}>{cancelText}</Button>
        <Button variant="contained" onClick={onConfirm}>
          {confirmText}
        </Button>
      </Box>
    </Dialog>
  );
};

export default ConfirmPopup;
