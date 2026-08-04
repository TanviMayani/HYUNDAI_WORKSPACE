import { createApi } from "@reduxjs/toolkit/query/react";
import { COMMON_API_URL } from "../../../constants/apiUrls";
import { axiosBaseQuery } from "../../../utils/helper";

export const profileApis = createApi({
  baseQuery: axiosBaseQuery({
    baseUrl: ``,
  }),
  reducerPath: "profile",
  keepUnusedDataFor: 5,
  refetchOnMountOrArgChange: true,
  endpoints: (builder) => ({
    getProfile: builder.query<any, any>({
      query: () => {
        return {
          method: "get",
          url: `${COMMON_API_URL.getUserProfile}`,
        };
      },
      //providesTags: ['Profile']
    }),
    updateProfile: builder.mutation({
      query: (data) => {
        return {
          url: `${COMMON_API_URL.updateUserProfile}`,
          method: "patch",
          data: data,
        };
      },
    }),
    updateProfileSetting: builder.mutation({
      query: ({ data }) => {
        return {
          url: `${COMMON_API_URL.updateUserProfileSetting}`,
          method: "patch",
          data: { ...data },
        };
      },
    }),
    updateProfilePassword: builder.mutation({
      query: ({ data }) => {
        return {
          url: `${COMMON_API_URL.updateUserPasswordSetting}`,
          method: "patch",
          data: { ...data },
        };
      },
    }),
  }),
});
export const {
  useGetProfileQuery,
  useUpdateProfileMutation,
  useUpdateProfileSettingMutation,
  useUpdateProfilePasswordMutation,
} = profileApis;
