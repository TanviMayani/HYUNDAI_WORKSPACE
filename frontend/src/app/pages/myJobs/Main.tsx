import { useEffect, useState } from "react";
import MainBox from "../../components/MainBox";
import {
  Box,
  Grid,
  Typography,
  Button,
  Stack,
  FormControlLabel,
  Checkbox,
  TextField,
} from "@mui/material";
import PdfCard from "./PdfCard";
import UploadComponent from "../../components/UploadComponent";
import toast from "react-hot-toast";
import {
  useCreateJobMutation,
  useListMethodQuery,
} from "../../redux/features/jobs";
import { useNavigate } from "react-router-dom";
import useFileUpload from "../../utils/hooks/useFileUpload";
import InputLabel from "@mui/material/InputLabel";
import MenuItem from "@mui/material/MenuItem";
import FormControl from "@mui/material/FormControl";
import Select, { SelectChangeEvent } from "@mui/material/Select";

const Main = () => {
  const [extract, setExtract] = useState([
    "line",
    "forms",
    "table",
    "signature",
    "barcode",
  ]);
  const allowedTypes = ["application/pdf", "image/jpeg", "image/png"];
  const navigate = useNavigate();
  const [files, setFiles] = useState<File[]>([]);
  const { handleFileChange } = useFileUpload(files, setFiles, {
    allowedTypes,
  });

  const [createJob, { isLoading, isSuccess, isError }] = useCreateJobMutation();
  const { data: methodData, refetch } = useListMethodQuery({});

  const [options, setOptions] = useState("");

  const [name, setName] = useState("");

  const handleChange = (event: SelectChangeEvent) => {
    setOptions(event.target?.value);
  };

  const handleCheckboxChange = (value) => {
    const isChecked = extract.includes(value);
    if (isChecked) {
      setExtract(extract.filter((item) => item !== value));
    } else {
      setExtract([...extract, value]);
    }
  };

  const handleClick = (event) => {
    event.preventDefault();
    if (!name) {
      toast.error("Job name is required");
      return;
    }
    const formData = new FormData();
    formData.append("extract", JSON.stringify(extract));
    formData.append("job_name", name);
    formData.append("method_id", options?.id);
    files.forEach((file) => formData.append("files", file));
    createJob(formData);
  };

  const handleDelete = (item) => {
    const filterData = files?.filter((ele) => ele?.name !== item?.name);
    setFiles(filterData);
  };

  useEffect(() => {
    if (isSuccess) {
      toast.success("Job Created Successfully.");
      navigate("/dashboard/my-jobs");
    }
    isError && toast.error("Something went wrong!");
  }, [isSuccess, isError]);

  useEffect(() => {
    refetch();
  }, []);

  return (
    <MainBox>
      <Box
        p={3}
        pb={8}
        sx={{ width: "100%", maxHeight: "100%", maxWidth: "800px" }}
        display={"flex"}
        flexDirection={"column"}
        justifyContent={"space-between"}
        mx={"auto"}
      >
        <Typography
          variant="h5"
          fontWeight={"bold"}
          textAlign={"center"}
          mt={2}
          mb={4}
        >
          Upload Files
        </Typography>
        <Grid container spacing={5} justifyContent={"center"}>
          <Grid item md={6} xs={12}>
            <UploadComponent handleChange={handleFileChange} />
          </Grid>
          <Grid item md={6} xs={12}>
            <Box>
              <Stack>
                <Grid item xs={12} mb={2}>
                  <TextField
                    required
                    fullWidth
                    id="name"
                    placeholder="Job Name"
                    size="small"
                    name="name"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                  />
                </Grid>
                <Box
                  display={"flex"}
                  alignItems={"center"}
                  flexWrap="wrap"
                  gap={2}
                >
                  <FormControl fullWidth>
                    <InputLabel id="demo-simple-select-label">
                      Select Model
                    </InputLabel>
                    <Select
                      labelId="demo-simple-select-label"
                      id="demo-simple-select"
                      value={options} // Use the state here
                      label="Select Model"
                      onChange={handleChange}
                    >
                      {methodData?.length > 0 &&
                        methodData.map((item) => (
                          <MenuItem key={item?.id} value={item}>
                            {item?.display_name}
                          </MenuItem>
                        ))}
                    </Select>
                  </FormControl>

                  {options?.display_name === "Standard Extraction" && (
                    <Box>
                      <Typography variant="body1" fontWeight={"bold"}>
                        Extract
                      </Typography>
                      {["line", "forms", "table", "signature", "barcode"]?.map(
                        (item) => {
                          return (
                            <FormControlLabel
                              control={
                                <Checkbox
                                  className="secondary-pink"
                                  value={item}
                                  size="small"
                                  checked={extract.includes(item)}
                                  onChange={() => handleCheckboxChange(item)}
                                />
                              }
                              label={item}
                            />
                          );
                        }
                      )}
                    </Box>
                  )}
                </Box>
                <Box my={2} display={"flex"} justifyContent={"center"}>
                  <Button
                    variant="contained"
                    disabled={!files?.length || isLoading}
                    onClick={handleClick}
                    fullWidth
                  >
                    Create Job
                  </Button>
                </Box>
              </Stack>
            </Box>
          </Grid>
        </Grid>
        {files?.length > 0 && (
          <Grid item md={12} xs={12}>
            <PdfCard data={files} onItemChange={handleDelete} />
          </Grid>
        )}
      </Box>
    </MainBox>
  );
};

export default Main;
