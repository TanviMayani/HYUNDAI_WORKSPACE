import {
  Grid,
  Paper,
  Typography,
  Box,
  Stack,
  Button,
  IconButton,
  InputBase,
  Divider,
} from "@mui/material";
import AddCircleIcon from "@mui/icons-material/AddCircle";
import {
  useFilterJobsQuery,
  useGetAllJobsQuery,
} from "../../redux/features/jobs";
import { useEffect, useMemo, useState } from "react";
import JobCard from "./JobCard";
import { useNavigate } from "react-router-dom";
import { cloneDeep } from "lodash";
import { useParams } from "react-router-dom";
import DocViewer from "./DocViewer";
import OutputViewer, { NoOutput } from "./OutputViewer";
import DocViewOutput from "./DocViewOutput";
import FilterAltIcon from "@mui/icons-material/FilterAlt";
import SearchIcon from "@mui/icons-material/Search";
import CenterIcon from "../../components/CenterIcon";
import CompareIcon from "@mui/icons-material/Compare";
import { LocalizationProvider } from "@mui/x-date-pickers/LocalizationProvider";
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs";
import { DatePicker } from "@mui/x-date-pickers/DatePicker";
import dayjs from "dayjs";
import DocDrawer from "./DocDrawer";
import DocLoader from "../../components/DocLoader";

export default function ViewJobs() {
  const navigate = useNavigate();
  const { viewId } = useParams();
  const [isComapre, setIsCompare] = useState(false);
  const [isFilter, setIsFilter] = useState(false);
  const [polling, setPolling] = useState(false);
  const [isFilterSkip, setFilterSkip] = useState(true);
  const [search, setSearch] = useState("");
  const [startDate, setStartDate] = useState(null);
  const [endDate, setEndDate] = useState(null);

  const {
    data: allJobs,
    refetch,
    isLoading: jobLoading,
  } = useGetAllJobsQuery({}, { pollingInterval: polling ? 3000 : 0 });

  const { data: filterData } = useFilterJobsQuery(
    {
      startDate: dayjs(startDate).format("YYYY-MM-DD"),
      endDate: dayjs(endDate).format("YYYY-MM-DD"),
    },
    { skip: isFilterSkip }
  );

  const [openDrawer, setOpenDrawer] = useState<boolean>(false);

  const [documentId, setDocumentId] = useState("");
  const [page, setPage] = useState(1);

  const data = useMemo(() => {
    let sourceList = !isFilterSkip && filterData ? filterData : allJobs;
    let list = sourceList?.length ? cloneDeep(sourceList) : [];
    if (search.trim()) {
      const q = search.toLowerCase();
      list = list.filter(
        (job: any) =>
          job?.job_name?.toLowerCase().includes(q) ||
          job?.method?.toLowerCase().includes(q) ||
          job?.status?.toLowerCase().includes(q) ||
          job?.source?.some((s: any) => s?.name?.toLowerCase().includes(q))
      );
    }
    return list;
  }, [allJobs, filterData, isFilterSkip, search]);

  useEffect(() => {
    if (startDate && endDate) {
      setFilterSkip(false);
    }
  }, [startDate, endDate]);

  const openJob = (e, job) => {
    e.preventDefault();
    navigate(job?.job_id);
  };

  useEffect(() => {
    refetch();
  }, []);

  useEffect(() => {
    const hasProcessing = data?.some(
      (job) => job?.status === "Pending" || job?.status === "In_Process"
    );
    setPolling(hasProcessing);
  }, [data]);

  return (
    <>
      <Box mt={12} mx={3} mb={4}>
        <Grid container spacing={3}>
          {!isComapre && (
            <Grid item xs={12} md={12} lg={4}>
              <Stack
                direction="row"
                justifyContent={"space-between"}
                alignItems="flex-end"
                mb={2}
              >
                <Typography variant="h6" color={"primary"}>
                  Jobs
                </Typography>
                <Button
                  variant="contained"
                  startIcon={<AddCircleIcon />}
                  onClick={() => setOpenDrawer(true)}
                  size="small"
                  sx={{ py: 0.5, px: 2 }}
                >
                  Add Job
                </Button>
              </Stack>

              <Paper
                elevation={0}
                className="deafultShadow"
                sx={{
                  height: "100%",
                  minHeight: "200px",
                  overflow: "auto",
                }}
              >
                {viewId === undefined && (
                  <Box position={"relative"}>
                    <Paper
                      elevation={0}
                      className="defaultShadow"
                      component="form"
                      sx={{
                        p: "0 4px",
                        display: "flex",
                        alignItems: "center",
                        height: "50px",
                        width: "100%",
                        background: "white",
                        mb: 2,
                      }}
                    >
                      <IconButton sx={{ p: "10px" }} aria-label="menu">
                        <SearchIcon />
                      </IconButton>
                      <InputBase
                        sx={{ ml: 1, flex: 1 }}
                        placeholder="Search Jobs"
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        inputProps={{ "aria-label": "search google maps" }}
                      />

                      <Divider
                        sx={{ height: 28, m: 0.5 }}
                        orientation="vertical"
                      />
                      <IconButton
                        color="primary"
                        sx={{ p: "10px" }}
                        aria-label="directions"
                      >
                        <CenterIcon>
                          <FilterAltIcon
                            onClick={() => setIsFilter(!isFilter)}
                          />
                        </CenterIcon>
                      </IconButton>
                    </Paper>

                    {isFilter && (
                      <Paper
                        elevation={0}
                        className="defaultShadow"
                        sx={{
                          p: 3,
                          alignItems: "center",
                          bgcolor: "white",
                          width: "50%",
                          background: "white",
                          mb: 2,
                          position: "absolute",
                          zIndex: 9,
                          right: 0,
                        }}
                      >
                        <Box display={"flex"} flexDirection={"column"} gap={2}>
                          <LocalizationProvider dateAdapter={AdapterDayjs}>
                            <DatePicker
                              label="Start Date"
                              value={startDate}
                              onChange={(newValue) => {
                                if (newValue) {
                                  setStartDate(newValue);
                                }
                              }}
                            />
                            <DatePicker
                              label="End Date"
                              value={endDate}
                              onChange={(newValue) => {
                                if (newValue) {
                                  setEndDate(newValue);
                                }
                              }}
                            />
                          </LocalizationProvider>
                        </Box>
                      </Paper>
                    )}
                  </Box>
                )}
                {viewId !== undefined ? (
                  <DocViewer id={viewId} onDocument={setDocumentId} />
                ) : (
                  <>
                    <Box height="65vh">
                      {jobLoading ? (
                        <DocLoader />
                      ) : (
                        <>
                          {data?.length > 0 ? (
                            data?.map((jobData, index) => {
                              return (
                                <Box key={index}>
                                  <JobCard
                                    key={index}
                                    data={jobData}
                                    onClick={openJob}
                                    refetch={refetch}
                                  />
                                </Box>
                              );
                            })
                          ) : (
                            <NoOutput />
                          )}
                        </>
                      )}
                    </Box>
                  </>
                )}
              </Paper>
            </Grid>
          )}
          <DocViewOutput
            id={documentId}
            onPage={setPage}
            page={page}
            isComapre={isComapre}
          />
          <Grid item xs={12} md={12} lg={isComapre ? 6 : 4}>
            <Box
              display={"flex"}
              justifyContent={"space-between"}
              alignItems={"center"}
              mb={2}
            >
              <Typography variant="h6" fontWeight={"600"} color={"primary"}>
                Output
              </Typography>
              {isComapre && <CenterIcon>COMPARE MODE ON</CenterIcon>}
              {documentId && (
                <CenterIcon>
                  <CompareIcon onClick={() => setIsCompare(!isComapre)} />
                </CenterIcon>
              )}
            </Box>
            <Paper
              elevation={0}
              sx={{
                height: "80vh",
              }}
            >
              <OutputViewer id={documentId} page={page} />
            </Paper>
          </Grid>
        </Grid>
      </Box>
      <DocDrawer
        open={openDrawer}
        closeDrawer={() => setOpenDrawer(false)}
        refetch={refetch}
      />
    </>
  );
}

//extra keys on extract modal backend

//ITR uploded check ITR alert text

// Finance
// claim
// policy
