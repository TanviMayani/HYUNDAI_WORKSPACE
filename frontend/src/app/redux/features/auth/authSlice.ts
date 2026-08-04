/* eslint-disable @typescript-eslint/no-explicit-any */
import { createSlice } from "@reduxjs/toolkit";
import {
  forgotPassword,
  login,
  register,
  resetPassword,
} from "./authApi";

const initialState: any = {
  login: {
    data: null,
    status: "idle",
  },
  register: {
    data: null,
    status: "idle",
  },
  forgotPassword: {
    data: null,
    status: "idle",
  },
  resetPassword: {
    data: null,
    status: "idle",
  },
  resendEmailVerify: {
    data: null,
    status: "idle",
  },
  verifyPasswordToken: {
    data: null,
    status: "idle",
  },
};

const authSlice = createSlice({
  initialState,
  name: "authSlice",
  reducers: {},
  extraReducers: (builder) => {
    builder.addCase(login.pending, (state) => {
      state.login.status = "pending";
    });
    builder.addCase(login.fulfilled, (state, action) => {
      state.login.status = "succeeded";
      state.login.data = action.payload;
    });
    builder.addCase(login.rejected, (state, action) => {
      state.login.status = "failed";
      state.login.data = action.error.message;
    });
    builder.addCase(register.pending, (state) => {
      state.register.status = "pending";
    });
    builder.addCase(register.fulfilled, (state, action) => {
      state.register.status = "succeeded";
      state.register.data = action.payload;
    });
    builder.addCase(register.rejected, (state, action) => {
      state.register.status = "failed";
      state.register.data = action.error.message;
    });
    builder.addCase(forgotPassword.pending, (state) => {
      state.forgotPassword.status = "pending";
    });
    builder.addCase(forgotPassword.fulfilled, (state, action) => {
      state.forgotPassword.status = "succeeded";
      state.forgotPassword.data = action.payload;
    });
    builder.addCase(forgotPassword.rejected, (state, action) => {
      state.forgotPassword.status = "failed";
      state.forgotPassword.data = action.error.message;
    });
    builder.addCase(resetPassword.pending, (state) => {
      state.resetPassword.status = "pending";
    });
    builder.addCase(resetPassword.fulfilled, (state, action) => {
      state.resetPassword.status = "succeeded";
      state.resetPassword.data = action.payload;
    });
    builder.addCase(resetPassword.rejected, (state, action) => {
      state.resetPassword.status = "failed";
      state.resetPassword.data = action.error.message;
    });
  },
});
export default authSlice.reducer;
