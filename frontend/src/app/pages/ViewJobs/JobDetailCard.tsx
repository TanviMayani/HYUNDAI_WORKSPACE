import { Box, Chip, Divider, Grid, Typography } from "@mui/material";
import dayjs from "dayjs";
import { JobStatus } from "../../constants/jobStatus";
const JobDetailCard = ({ data }: any) => {
  return (
    <>
      <Grid container wrap="nowrap" spacing={2} p={2}>
        <Grid item xs>
          <Box display={"flex"} justifyContent={"space-between"}>
            <Typography variant="body1" fontWeight={"600"}>
              {data?.job_name}
            </Typography>
            <Chip
              label={data?.status}
              color={
                data.status === JobStatus.Error
                  ? "error"
                  : data.status === JobStatus.Completed
                  ? "success"
                  : "warning"
              }
              variant="outlined"
              className="defaultRadius"
            />
          </Box>
          <Box display={"flex"} justifyContent={"space-between"} mt={0.5}>
            <Typography variant="caption" fontWeight={"600"}>
              Document : {data?.process === "single" ? 1 : 10}
            </Typography>
            <Typography variant="caption" fontWeight={"600"}>
              {dayjs(data?.job_start_time)?.format("DD/MM/YYYY")}
            </Typography>
          </Box>
        </Grid>
      </Grid>
      <Divider />
    </>
  );
};

export default JobDetailCard;
