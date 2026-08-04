import { Box, Menu, MenuItem, Typography } from "@mui/material";
import dayjs from "dayjs";
import CalendarMonthIcon from "@mui/icons-material/CalendarMonth";
import toast from "react-hot-toast";
import MoreVertIcon from "@mui/icons-material/MoreVert";
import { useDeleteJobMutation } from "../../redux/features/jobs";
import ConfirmPopup from "../../components/Popup/ConfirmPopup";
import { useEffect, useState, useCallback } from "react";

const JobCard = ({ data, onClick, refetch }) => {
  const [menuAnchor, setMenuAnchor] = useState(null);
  const [isDeletePopupOpen, setDeletePopupOpen] = useState(false);
  const [deleteJob, { isSuccess, isError }] = useDeleteJobMutation();

  const isMenuOpen = Boolean(menuAnchor);

  const handleMenuClick = useCallback((event) => {
    setMenuAnchor(event.currentTarget);
  }, []);

  const handleMenuClose = useCallback(() => {
    setMenuAnchor(null);
  }, []);

  const handleDeleteClick = useCallback((event) => {
    event.stopPropagation();
    setDeletePopupOpen(true);
  }, []);

  const confirmDelete = useCallback(() => {
    deleteJob(data?.job_id);
  }, [data, deleteJob]);

  useEffect(() => {
    if (isSuccess) {
      toast.success("Instance deleted successfully");
      setDeletePopupOpen(false);
      refetch();
    } else if (isError) {
      toast.error("Something went wrong!");
      setDeletePopupOpen(false);
    }
  }, [isSuccess, isError, refetch]);

  const handleCardClick = useCallback(
    (event) => {
      if (data?.status !== "Pending" && data?.status !== "In_Process") {
        onClick(event, data);
      } else {
        toast.error("Status is still processing. Please wait...");
      }
    },
    [data, onClick]
  );

  return (
    <>
      <Box
        bgcolor="white"
        mb={2}
        p={2}
        borderRadius={2}
        className="defaultShadow"
        onClick={handleCardClick}
        sx={{ cursor: "pointer" }}
      >
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Typography
            variant="h6"
            fontSize={10}
            textTransform="uppercase"
            color="primary"
            border="1px solid #e3e3e3"
            px={1}
          >
            {data?.method}
          </Typography>

          <Box
            pl={2}
            onClick={(event) => {
              event.stopPropagation(); // Prevent parent onClick
              handleMenuClick(event);
            }}
          >
            <MoreVertIcon sx={{ fontSize: 16, cursor: "pointer" }} />
          </Box>
          <Menu
            id="job-card-menu"
            anchorEl={menuAnchor}
            open={isMenuOpen}
            onClose={handleMenuClose}
            MenuListProps={{ "aria-labelledby": "menu-button" }}
          >
            <MenuItem onClick={handleDeleteClick}>Delete</MenuItem>
          </Menu>
        </Box>

        <Box display="flex" justifyContent="space-between" gap={1}>
          <Box>
            <Typography
              variant="h6"
              fontSize={16}
              fontWeight="bold"
              color="primary"
            >
              {data?.job_name}
            </Typography>
            <Typography variant="h6" fontSize={11} color="primary">
              {data?.id}
            </Typography>
          </Box>
          <span
            className={
              data?.status === "Completed"
                ? "chip-success"
                : data?.status === "Failed"
                ? "chip-error"
                : "chip-warning"
            }
          >
            {data?.status}
          </span>
        </Box>

        <Box display="flex" justifyContent="space-between" mt={1}>
          <Typography color="#555" fontSize={14} fontWeight="bold">
            Documents:{" "}
            <span className="secondary-pink">{data?.source?.length}</span>
          </Typography>
          <Typography
            variant="caption"
            fontWeight="600"
            display="flex"
            alignItems="center"
            gap={1}
          >
            <span>
              {dayjs(data?.job_start_time).format("DD/MM/YYYY hh:mm A")}
            </span>
            <CalendarMonthIcon sx={{ color: "#666" }} />
          </Typography>
        </Box>
      </Box>

      <ConfirmPopup
        open={isDeletePopupOpen}
        onClose={() => setDeletePopupOpen(false)}
        onConfirm={confirmDelete}
        title="Are you sure you want to delete this instance?"
      />
    </>
  );
};

export default JobCard;
