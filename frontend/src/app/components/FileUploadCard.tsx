import CancelIcon from "@mui/icons-material/Cancel";
import {
  Box,
  Divider,
  IconButton,
  LinearProgress,
  Paper,
  Typography,
} from "@mui/material";
import { useState } from "react";
import { VscFilePdf } from "react-icons/vsc";
import ConfirmPopup from "../components/Popup/ConfirmPopup";
import { extractDataFromUrl, formatBytes } from "../utils/functions.js";
import useFileUploadProgress from "../utils/hooks/useFileUploadProgress.js";

const FileUploadCard = ({ item, onDataChange, editable = false }) => {
  const progress = useFileUploadProgress({ size: item?.size });
  const [open, setOpen] = useState(false);
  const urlName = item?.doc_url && extractDataFromUrl(item?.doc_url);

  const handleDelete = () => {
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
  };

  const handleConfirm = () => {
    onDataChange(item);
    handleClose();
  };

  return (
    <>
      <Paper elevation={0} sx={paperStyle}>
        <Box display={"flex"} alignItems={"center"} gap={1}>
          <VscFilePdf style={{ color: "red", fontSize: "15px" }} />
          <Typography fontSize={13}>
            {item?.name?.slice(0, 30) || urlName.slice(0, 30)}
          </Typography>
        </Box>
        <Box display={"flex"} alignItems={"center"} gap={1}>
          {!item?.doc_url && (
            <Typography fontSize={12}>{formatBytes(item?.size)}</Typography>
          )}
          {!editable && (
            <>
              <Divider orientation="vertical" flexItem />
              <IconButton
                aria-label="delete"
                size="small"
                onClick={handleDelete}
              >
                <CancelIcon />
              </IconButton>
            </>
          )}
        </Box>
      </Paper>
      {!item?.doc_url && (
        <LinearProgress
          variant="determinate"
          value={Math.round(progress)}
          color="secondary"
          sx={{ mb: 2, width: "100%" }}
        />
      )}
      <ConfirmPopup
        open={open}
        onConfirm={handleConfirm}
        onClose={handleClose}
        title="Are you sure to delete this File?"
      />
    </>
  );
};

export default FileUploadCard;

const paperStyle = {
  display: "flex",
  bgcolor: "white",
  width: "100%",
  p: 0.5,
  justifyContent: "space-between",
  borderRadius: "4px",
  mb: 0,
  border: "1px solid #e3e3e3",
};
