import { Password } from "@mui/icons-material";
import {
  Box,
  Button,
  TextField,
  Typography,
  Divider,
  InputAdornment,
} from "@mui/material";
import { useResetPasswordMutation } from "../../redux/features/commonApis";
import { useFormik } from "formik";
import * as yup from "yup";
import toast from "react-hot-toast";
import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import VisibilityIcon from "@mui/icons-material/Visibility";
import VisibilityOffIcon from "@mui/icons-material/VisibilityOff";
import HttpsIcon from "@mui/icons-material/Https";
import { useState } from "react";

const formikSchema = yup.object().shape({
  password: yup.string().nullable().required("Password is Required"),
  confirm_password: yup
    .string()
    .nullable()
    .required("Confirm Password is Required"),
});

const ResetPasswordForm = () => {
  const urlToken = window.location.search.split("=")[1];
  const navigate = useNavigate();
  const [resetPassword, { isSuccess, isLoading }] = useResetPasswordMutation();

  const [isPassShow, setIsPassShow] = useState(false);
  const [isConfirmPassShow, setIsConfirmPassShow] = useState(false);

  const formik = useFormik({
    initialValues: {
      password: "",
      confirm_password: "",
    },
    validationSchema: formikSchema,
    onSubmit: (values) => {
      if (values.password === values.confirm_password) {
        if (!urlToken) {
          toast.error("Invalid Token Request");
          return;
        } else {
          resetPassword({ ...values, token: urlToken });
        }
      } else {
        toast.error("Password not matched");
      }
    },
  });

  useEffect(() => {
    isLoading && toast.loading("Loading...");

    if (isSuccess) {
      toast.success("Password reset successfully");
      navigate("/login");
    }
  }, [isSuccess, isLoading]);

  return (
    <Box
      sx={{
        width: "80%",
        height: "100%",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <Box
        sx={{
          p: 3,
          borderRadius: "8px",
          display: "flex",
          flexDirection: "column",
          boxShadow: `0px 3px 12px 0px rgba(0, 0, 0, 0.19)`,
        }}
      >
        <Typography component="h1" variant="h5" fontWeight={"bold"}>
          Reset Password
        </Typography>
        <Typography component="h2" variant="subtitle2" color={"secondary"}>
          {`Create New Password`}
        </Typography>
        <Divider sx={{ my: 1, pt: 2 }} />
        <Box
          component="form"
          onSubmit={formik.handleSubmit}
          noValidate
          sx={{ mt: 1 }}
        >
          <TextField
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <HttpsIcon />
                </InputAdornment>
              ),
              endAdornment: (
                <InputAdornment
                  position="start"
                  onClick={() => setIsPassShow((prev) => !prev)}
                >
                  {!isPassShow ? <VisibilityIcon /> : <VisibilityOffIcon />}
                </InputAdornment>
              ),
            }}
            margin="normal"
            required
            fullWidth
            name="password"
            placeholder="New Password"
            type={isPassShow ? "text" : "password"}
            id="password"
            size="small"
            autoComplete="current-password"
            value={formik.values.password}
            onChange={formik.handleChange}
            error={!!(formik.touched.password && formik.errors.password)}
            helperText={formik.touched.password && formik.errors.password}
          />
          <TextField
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <HttpsIcon />
                </InputAdornment>
              ),
              endAdornment: (
                <InputAdornment
                  position="start"
                  onClick={() => setIsConfirmPassShow((prev) => !prev)}
                >
                  {!isConfirmPassShow ? (
                    <VisibilityIcon />
                  ) : (
                    <VisibilityOffIcon />
                  )}
                </InputAdornment>
              ),
            }}
            margin="normal"
            required
            type={isConfirmPassShow ? "text" : "password"}
            fullWidth
            name="confirm_password"
            placeholder="Confirm Password"
            size="small"
            id="confirm_password"
            autoComplete="current-password"
            value={formik.values.confirm_password}
            onChange={formik.handleChange}
            error={
              !!(
                formik.touched.confirm_password &&
                formik.errors.confirm_password
              )
            }
            helperText={
              formik.touched.confirm_password && formik.errors.confirm_password
            }
          />
          <Box display="flex" justifyContent="flex-end">
            {" "}
            <Button
              type="submit"
              variant="contained"
              sx={{ my: 3, px: 6 }}
              disabled={isLoading}
            >
              Submit
            </Button>
          </Box>
        </Box>
      </Box>
    </Box>
  );
};

export default ResetPasswordForm;
