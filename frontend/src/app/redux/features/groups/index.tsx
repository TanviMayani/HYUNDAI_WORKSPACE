import { createApi } from "@reduxjs/toolkit/query/react";
import { COMMON_API_URL } from "../../../constants/apiUrls";
import { axiosBaseQuery } from "../../../utils/helper";

export const groupsApis = createApi({
  baseQuery: axiosBaseQuery({
    baseUrl: ``,
  }),
  reducerPath: "groups",
  keepUnusedDataFor: 5,
  refetchOnMountOrArgChange: true,
  endpoints: (builder) => ({
    getGroup: builder.query<any, any>({
      query: (args) => {
        const { id } = args;
        return {
          method: "get",
          url: `${COMMON_API_URL.getGroup}/${id}`,
        };
      },
     
    }),
    getAllGroups: builder.query<any, any>({
      query: () => {
        return {
          method: "get",
          url: `${COMMON_API_URL.getGroups}`,
        };
      },
      
    }),
    updateGroup: builder.mutation({
      query: ({ data }) => {
        const { id } = data;
        return {
          url: `${COMMON_API_URL.getGroup}/${id}`,
          method: "patch",
          data: { ...data },
        };
      },
    }),
    createGroup: builder.mutation({
      query: ({ data }) => {
        return {
          url: `${COMMON_API_URL.createGroup}`,
          method: "post",
          data: { ...data },
        };
      },
    }),
    deleteGroup: builder.mutation({
      query: (data) => {
        return {
          url: `${COMMON_API_URL.deleteGroup}/${data}`,
          method: "delete",
        };
      },
    })
  }),
});
export const {
  useCreateGroupMutation,
  useGetAllGroupsQuery,
  useGetGroupQuery,
  useUpdateGroupMutation,
  useDeleteGroupMutation,
} = groupsApis;
