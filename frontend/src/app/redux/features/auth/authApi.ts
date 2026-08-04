/* eslint-disable @typescript-eslint/no-explicit-any */
import axiosInstance from "../../../utils/axiosInstance";
import { COMMON_API_URL } from "../../../constants/apiUrls";
import { createAsyncThunk } from "@reduxjs/toolkit";
import { AxiosResponse } from "axios";

export const login : any = createAsyncThunk("authSlice/login", async (data: any) => {
  const request = { ...data.body };
  const result = await axiosInstance.post(COMMON_API_URL.login, request);
  return result;
});

export const register: any = createAsyncThunk(
  "authSlice/register",
  async (data: any) => {
    const request = { ...data.body };
    const result = await axiosInstance.post(COMMON_API_URL.register, request);
    return result;
  }
);



export const forgotPassword: any = createAsyncThunk(
  "authSlice/forgotPassword",
  async (data: any) => {
    const request = { ...data.body };
    const result = await axiosInstance.post(
      COMMON_API_URL.forgotPassword,
      request
    );
    return result;
  }
);

export const resetPassword: any = createAsyncThunk(
  "authSlice/resetPassword",
  async (data: any) => {
    const request = { ...data.body };
    const result = await axiosInstance.post(
      COMMON_API_URL.resetPassword,
      request
    );
    return result;
  }
);

