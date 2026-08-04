import {
  Box,
  Button,
  Divider,
  IconButton,
  InputAdornment,
  TextField,
  Typography,
} from "@mui/material";
import { useFormik } from "formik";

import { RemoveRedEye, VisibilityOff } from "@mui/icons-material";
import AlternateEmailIcon from "@mui/icons-material/AlternateEmail";
import { useCallback, useEffect, useState } from "react";
import toast from "react-hot-toast";
import { Link, useNavigate } from "react-router-dom";
import PassIcon from "../../../assets/password.svg";
import { useLoginMutation } from "../../redux/features/commonApis.js";
import { tokenEncrypt } from "../../utils/tokenEncrypter.js";
import { formikSchema } from "./constant";

const LoginForm = () => {
  const [login, { data, isSuccess, isError, isLoading, error }] =
    useLoginMutation();
  const [showPassword, setShowPassword] = useState(false);
  const navigate = useNavigate();

  const makeUserLoggedIn = useCallback((): void => {
    const rawToken = data?.token || data?.detail?.[0]?.data?.token;
    if (rawToken) {
      const encryptedToken = tokenEncrypt(rawToken);
      sessionStorage.setItem("token", encryptedToken);
      navigate("/dashboard/my-jobs");
    } else {
      toast.error("Failed to retrieve authentication token.");
    }
  }, [data, navigate]);

  const toogleShowPassword = () => {
    setShowPassword(!showPassword);
  };

  const formik = useFormik({
    initialValues: {
      email: "",
      password: "",
    },
    validationSchema: formikSchema,
    onSubmit: (values) => {
      login(values);
    },
  });

  useEffect(() => {
    if (isSuccess) {
      makeUserLoggedIn();
    }
    if (isError) {
      const errMsg = (error as any)?.message || (error as any)?.data || "Login failed";
      toast.error(typeof errMsg === "string" ? errMsg : "Login failed");
    }
  }, [isSuccess, isError]);

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
        <Typography component="h1" variant="h5" fontWeight={"bold"}>
          Welcome Back !
        </Typography>
        <Typography component="h2" variant="subtitle2" color={"secondary"}>
          {`Login to your account`}
        </Typography>
        <Divider sx={{ my: 1, pt: 2 }} />
        <Box component="form" onSubmit={formik.handleSubmit} sx={{ mt: 1 }}>
          <TextField
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <AlternateEmailIcon />
                </InputAdornment>
              ),
            }}
            margin="normal"
            required
            fullWidth
            id="email"
            label="Email Address"
            name="email"
            autoComplete="off"
            autoFocus
            size="medium"
            value={formik.values.email}
            onChange={formik.handleChange}
            error={!!(formik.touched.email && formik.errors.email)}
            helperText={
              (formik.touched.email && formik.errors.email) ||
              "Allowed: @hilb.in, @binarysemantics.com"
            }
          />
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
            margin="normal"
            required
            fullWidth
            name="password"
            label=""
            type={showPassword ? "text" : "password"}
            id="password"
            size="medium"
            placeholder="Password"
            autoComplete="new-password"
            value={formik.values.password}
            onChange={formik.handleChange}
            error={!!(formik.touched.password && formik.errors.password)}
            helperText={formik.touched.password && formik.errors.password}
          />
          <Box sx={{ display: "flex", justifyContent: "flex-end" }}>
            <Button
              type="submit"
              variant="contained"
              sx={{ my: 3, px: 6 }}
              disabled={isLoading}
            >
              {isLoading ? "Loading..." : "Sign In"}
            </Button>
          </Box>
          <Divider sx={{ mb: 2 }} />

          <Box>
            <Typography
              variant="body2"
              component={"span"}
            >{`Don't have an account? `}</Typography>
            <Link to="/register" className="link">
              {"Create an Account"}
            </Link>
          </Box>
        </Box>
      </Box>

    </Box>
  );
};

export default LoginForm;
