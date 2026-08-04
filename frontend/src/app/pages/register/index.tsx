import {
  AlternateEmail,
  RemoveRedEye,
  VisibilityOff,
} from "@mui/icons-material";
import PersonIcon from "@mui/icons-material/Person";
import WorkIcon from "@mui/icons-material/Work";
import {
  Divider,
  IconButton,
  InputAdornment,
  Box,
  Button,
  Grid,
  TextField,
  Typography,
} from "@mui/material";
import { useFormik } from "formik";
import { useEffect, useState } from "react";
import ReCAPTCHA from "react-google-recaptcha";
import toast from "react-hot-toast";
import "react-phone-input-2/lib/bootstrap.css";
import { useDispatch, useSelector } from "react-redux";
import { Link, useNavigate } from "react-router-dom";
import * as yup from "yup";
import PassIcon from "../../../assets/password.svg";
import { API_CONSTANTS, messages } from "../../constants";
import { AppDispatch } from "../../redux";
import { register } from "../../redux/features/auth/authApi";

// TODO remove, this demo shouldn't need to reset the theme.

const formikSchema = yup.object().shape({
  first_name: yup.string().nullable().required("Required"),
  last_name: yup.string().nullable().required("Required"),
  email: yup
    .string()
    .email("Please write a valid email")
    .nullable()
    .required("Required"),
  password: yup
    .string()
    .nullable()
    .matches(
      /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/,
      "Password must contain at least 8 characters, one uppercase, one lowercase, one number, and one special character"
    )
    .required("Required"),
  confirm_password: yup
    .string()
    .nullable()
    .oneOf([yup.ref("password"), null], "Passwords must match")
    .required("Required"),
});

export default function RegisterForm() {
  const dispatch = useDispatch<AppDispatch>();
  const navigate = useNavigate();
  const [loading, setLoading] = useState<boolean>(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const toogleShowPassword = () => {
    setShowPassword(!showPassword);
  };
  const toogleCShowPassword = () => {
    setShowConfirmPassword(!showConfirmPassword);
  };
  {
    /* @ts-expect-error: this is the error */
  }
  const registerSelector = useSelector((state) => state.auth.register);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const formik = useFormik({
    initialValues: {
      first_name: "",
      last_name: "",
      email: "",
      password: "",
      confirm_password: "",
    },
    validationSchema: formikSchema,
    onSubmit: (values) => {
      if (values.password === values.confirm_password) {
        dispatch(
          register({
            body: {
              ...values,
            },
          })
        );
      }
    },
  });

  useEffect(() => {
    let toastId;
    if (registerSelector?.status === API_CONSTANTS.loading) {
      setLoading(true);
      toastId = toast.loading("processing");
    }
    if (registerSelector?.status === API_CONSTANTS.success && loading) {
      toast.dismiss(toastId);
      toast.success(messages.registrationSuccess);
      formik.resetForm();
      navigate("/login");
    }
    if (registerSelector?.status === API_CONSTANTS.error && loading) {
      setLoading(false);
      toast.dismiss(toastId);
      toast.error(registerSelector.data);
    }
  }, [registerSelector, navigate, loading, formik]);

  return (
    <Box
      display={"flex"}
      flexDirection={"column"}
      justifyContent={"center"}
      alignItems={"center"}
      sx={{
        width: "80%",
        height: "100%",
        maxWidth: "500px",
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
        <Typography
          component="h1"
          variant="h5"
          color={"primary"}
          sx={{ fontWeight: "bold" }}
        >
          {`Create an account !`}
        </Typography>
        <Typography component="h2" variant="subtitle2" color={"secondary"}>
          {`Register to your account`}
        </Typography>
        <Divider sx={{ my: 1, pt: 2 }} />
        <Box
          component="form"
          noValidate
          onSubmit={formik.handleSubmit}
          sx={{ mt: 3 }}
        >
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <TextField
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <PersonIcon />
                    </InputAdornment>
                  ),
                }}
                autoComplete="given-name"
                name="first_name"
                required
                fullWidth
                id="first_name"
                placeholder="First Name"
                size="medium"
                value={formik.values.first_name}
                onChange={formik.handleChange}
                error={
                  !!(formik.touched.first_name && formik.errors.first_name)
                }
                helperText={
                  formik.touched.first_name && formik.errors.first_name
                }
                autoFocus
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                required
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <PersonIcon />
                    </InputAdornment>
                  ),
                }}
                fullWidth
                id="last_name"
                placeholder="Last Name"
                size="small"
                name="last_name"
                value={formik.values.last_name}
                onChange={formik.handleChange}
                autoComplete="family-name"
                error={!!(formik.touched.last_name && formik.errors.last_name)}
                helperText={formik.touched.last_name && formik.errors.last_name}
              />
            </Grid>

            <Grid item xs={12}>
              <TextField
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <AlternateEmail />
                    </InputAdornment>
                  ),
                }}
                required
                fullWidth
                id="email"
                placeholder="Email Address"
                size="small"
                name="email"
                value={formik.values.email}
                onChange={formik.handleChange}
                autoComplete="email"
                error={!!(formik.touched.email && formik.errors.email)}
                helperText={formik.touched.email && formik.errors.email}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <img src={PassIcon} alt="password-icon" />
                    </InputAdornment>
                  ),
                  endAdornment: (
                    <IconButton onClick={toogleShowPassword}>
                      {showPassword ? <VisibilityOff /> : <RemoveRedEye />}
                    </IconButton>
                  ),
                }}
                required
                fullWidth
                name="password"
                placeholder="Password"
                size="small"
                type={showPassword ? "text" : "password"}
                id="password"
                autoComplete="new-password"
                value={formik.values.password}
                onChange={formik.handleChange}
                error={!!(formik.touched.password && formik.errors.password)}
                helperText={formik.touched.password && formik.errors.password}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                required
                fullWidth
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <img src={PassIcon} alt="password-icon" />
                    </InputAdornment>
                  ),
                  endAdornment: (
                    <IconButton onClick={toogleCShowPassword}>
                      {showConfirmPassword ? (
                        <VisibilityOff />
                      ) : (
                        <RemoveRedEye />
                      )}
                    </IconButton>
                  ),
                }}
                name="confirm_password"
                placeholder="Confirm Password"
                size="small"
                type={showConfirmPassword ? "text" : "password"}
                id="confirm_password"
                autoComplete="new-password"
                value={formik.values.confirm_password}
                onChange={formik.handleChange}
                error={
                  !!(
                    formik.touched.confirm_password &&
                    formik.errors.confirm_password
                  )
                }
                helperText={
                  formik.touched.confirm_password &&
                  formik.errors.confirm_password
                }
              />
            </Grid>
          </Grid>

          <Box display="flex" justifyContent="flex-end">
            <Button
              type="submit"
              variant="contained"
              sx={{ my: 3 }}
              disabled={loading}
            >
              Sign Up
            </Button>
          </Box>

          <Grid container justifyContent="center">
            <Grid item>
              <Typography
                component="span"
                variant="body2"
              >{`Already have an account? `}</Typography>
              <Link to="/login" className="link">
                Sign in
              </Link>
            </Grid>
          </Grid>
        </Box>
      </Box>
    </Box>
  );
}
