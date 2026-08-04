import { Close } from "@mui/icons-material";
import AddIcon from "@mui/icons-material/Add";
import CloudUploadIcon from "@mui/icons-material/CloudUpload";
import {
  Button,
  Checkbox,
  FormControl,
  FormControlLabel,
  IconButton,
  InputLabel,
  MenuItem,
  Select,
  TextField,
  Typography,
} from "@mui/material";
import Box from "@mui/material/Box";
import Drawer from "@mui/material/Drawer";
import { styled } from "@mui/material/styles";
import { useFormik } from "formik";
import { useEffect, useState } from "react";
import toast from "react-hot-toast";
import * as yup from "yup";
import DrawerLoader from "../../components/DrawerLoader.js";
import PdfCard from "./PdfCard.js";
import useFileUpload from "../../utils/hooks/useFileUpload.js";
import {
  useCreateJobMutation,
  useListMethodQuery,
} from "../../redux/features/jobs/index.js";
import { SelectChangeEvent } from "@mui/material/Select";
import SampleBox from "../../components/SampleBox.js";

const VisuallyHiddenInput = styled("input")({
  clip: "rect(0 0 0 0)",
  clipPath: "inset(50%)",
  height: 1,
  overflow: "hidden",
  position: "absolute",
  bottom: 0,
  left: 0,
  whiteSpace: "nowrap",
  width: 1,
});

const formikSchema = yup.object().shape({
  name: yup.string().nullable().required("Required"),
});
const drawerWidth = 480;

export default function DocDrawer({ open, closeDrawer, refetch }) {
  const allowedTypes = [
    "application/pdf",
    "image/jpeg",
    "image/png",
    "image/jpg",
  ];

  const [extract, setExtract] = useState([
    "line",
    "forms",
    "table",
    "signature",
    "barcode",
  ]);

  const [options, setOptions] = useState("");
  const [isSample, setIsSample] = useState(false);
  const [createJob, { isLoading, isSuccess, isError }] = useCreateJobMutation();

  const { data: methodData, refetch: methodFetch } = useListMethodQuery({});

  const [files, setFiles] = useState<File[]>([]);
  const { handleFileChange } = useFileUpload(files, setFiles, { allowedTypes });
  const [fileResponse, setFileResponse] = useState<File[]>([]);
  const [selectedExtract, setSelectedExtract] = useState("Bank Statement");

  const formik = useFormik({
    initialValues: {
      name: "",
      file: "",
    },
    validationSchema: formikSchema,
    onSubmit: async (values) => {
      if (files.length === 0) {
        toast.error("No files selected.");
        return;
      }
      const formData = new FormData();
      formData.append(
        "extract",
        options?.display_name === "Bank Statement Extraction"
          ? JSON.stringify([
              selectedExtract?.toLowerCase().replaceAll(" ", "_"),
            ])
          : JSON.stringify(extract)
      );
      formData.append("job_name", values?.name);
      formData.append("method_id", options?.id);

      files.forEach((file) => formData.append("file", file));

      createJob(formData);
    },
  });

  useEffect(() => {
    if (isSuccess) {
      toast.success("Instance Created Successfully");
      refetch();
      setFiles([]);
      setOptions("");
      formik?.setValues({ name: "" });
      closeDrawer();
    }
    isError && toast.error("Something went wrong!");
  }, [isSuccess, isError]);

  const handleDelete = (item) => {
    const filterData = files?.filter((ele) => ele?.name !== item?.name);
    setFiles(filterData);
  };

  useEffect(() => {
    if (!open) {
      setFiles([]);
    }
  }, [open]);

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

  const handleCheckChange = (item) => {
    setSelectedExtract((prev) => (prev === item ? "" : item)); // Toggle selection
  };

  useEffect(() => {
    methodFetch();
  }, []);

  return (
    <div>
      <Drawer
        anchor={"right"}
        open={open}
        sx={{
          "& .MuiDrawer-paper": {
            boxSizing: "border-box",
            width: drawerWidth,
            background: (theme) => theme.palette.common.white,
          },
        }}
      >
        <Box px={4} position={"relative"} width={"100%"} height={"100vh"}>
          {isLoading && <DrawerLoader />}
          <Box
            display={"flex"}
            justifyContent={"space-between"}
            alignItems={"center"}
            mt={2}
          >
            <Typography
              id="modal-modal-description"
              variant="h6"
              fontWeight={"600"}
            >
              Create Instance
            </Typography>
            <IconButton onClick={closeDrawer}>
              <Close />
            </IconButton>
          </Box>

          <Box
            component="form"
            onSubmit={formik.handleSubmit}
            noValidate
            sx={{ mt: 2 }}
          >
            <TextField
              margin="normal"
              required
              fullWidth
              id="name"
              sx={{ mt: 0 }}
              placeholder="Instance Name"
              name="name"
              value={formik.values.name}
              onChange={formik.handleChange}
              error={!!(formik.touched.name && formik.errors.name)}
              helperText={formik.touched.name && formik.errors.name}
            />

            <FormControl fullWidth sx={{ mt: 1 }}>
              <InputLabel id="demo-simple-select-label">
                Select Model
              </InputLabel>
              <Select
                sx={{ p: 0 }}
                labelId="demo-simple-select-label"
                id="demo-simple-select"
                value={options || ""}
                label="Select Model"
                onChange={handleChange}
              >
                {methodData?.length > 0 &&
                  methodData
                    .filter((item: any) => {
                      const name = item?.display_name?.toLowerCase() || "";
                      return name.includes("llm") || name.includes("msme");
                    })
                    .map((item: any) => (
                      <MenuItem key={item?.id} value={item}>
                        {item?.display_name}
                      </MenuItem>
                    ))}
              </Select>
            </FormControl>

            <Box
              display={"flex"}
              alignItems={"center"}
              flexWrap="wrap"
              gap={1}
              mt={1}
            >
              {options?.display_name === "Bank Statement Extraction" && (
                <Box>
                  <Typography variant="body1" fontWeight="bold">
                    Extract
                  </Typography>
                  {["Bank Statement", "Credit Card Statement"].map((item) => (
                    <FormControlLabel
                      key={item}
                      control={
                        <Checkbox
                          className="secondary-pink"
                          value={item}
                          size="small"
                          checked={selectedExtract === item}
                          onChange={() => handleCheckChange(item)}
                        />
                      }
                      label={item}
                    />
                  ))}
                </Box>
              )}
            </Box>

            <Box
              display={"flex"}
              alignItems={"center"}
              flexWrap="wrap"
              gap={1}
              mt={1}
            >
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
                              sx={{ px: 0.5, ml: 0.5 }}
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

            <Typography fontSize={"16px"} mt={1} mb={1}>
              Files
            </Typography>

            <Box
              display={"flex"}
              flexDirection={"column"}
              alignItems={"center"}
              mt={0}
              sx={{
                border: "1px dashed #e3e3e3",
              }}
              className="defaultRadius"
              px={3}
              py={2}
            >
              <Button
                component="label"
                role={undefined}
                variant="contained"
                tabIndex={-1}
                sx={{ py: 0.5 }}
                startIcon={<CloudUploadIcon />}
              >
                Upload file
                <VisuallyHiddenInput
                  type="file"
                  accept={
                    options?.display_name?.toLowerCase().includes("msme")
                      ? "image/jpeg, image/png, image/jpg, image/gif"
                      : "application/pdf"
                  }
                  onChange={handleFileChange}
                />
              </Button>
              <Typography fontSize={"12px"} mt={0.5}>
                {options?.display_name?.toLowerCase().includes("msme")
                  ? "Only Image Files Allowed. Size should be less than 5 MB."
                  : "Only PDF Files Allowed. Size should be less than 5 MB."}
              </Typography>
              {/* <Button
                component="label"
                role={undefined}
                variant="contained"
                tabIndex={-1}
                sx={{ py: 0.5 }}
                startIcon={<CloudUploadIcon />}
              >
                Upload file
                <VisuallyHiddenInput
                  type="file"
                  accept="application/pdf, image/jpeg, image/png, image/gif"
                  onChange={handleFileChange}
                />
              </Button>
              <Typography fontSize={"12px"} mt={0.5}>
                Only PDF Files Allowed. Size should be less than 5 MB.
              </Typography> */}
              {/* <Typography
                color={"secondary"}
                fontSize={"12px"}
                sx={{ cursor: "pointer" }}
                mt={0.5}
                onClick={() => setIsSample(true)}
              >
                Need Sample
              </Typography> */}
              {(files?.length > 0 || fileResponse?.length > 0) && (
                <PdfCard
                  data={files}
                  onItemChange={handleDelete}
                  fileResponse={fileResponse}
                  editable={false}
                />
              )}
            </Box>

            <Box
              position={"absolute"}
              sx={{ left: 0, bottom: 0, width: "100%" }}
            >
              <Box
                width="100%"
                display={"flex"}
                bgcolor={"white"}
                justifyContent={"flex-end"}
                py={2}
                gap={3}
                px={4}
              >
                <Button
                  type="submit"
                  variant="contained"
                  sx={{ px: 6 }}
                  startIcon={<AddIcon />}
                  disabled={isLoading}
                >
                  {isLoading ? "Loading..." : "Create Instance"}
                </Button>
                <Button
                  variant="outlined"
                  disabled={isLoading}
                  onClick={closeDrawer}
                  sx={{ px: 4 }}
                >
                  Cancel
                </Button>
              </Box>
            </Box>
          </Box>
        </Box>
      </Drawer>
      {/* <SampleBox
        open={isSample}
        onClose={() => setIsSample(false)}
        isDoc={true}
      /> */}
    </div>
  );
}
