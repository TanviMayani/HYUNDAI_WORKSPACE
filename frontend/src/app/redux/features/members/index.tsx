import { createApi } from "@reduxjs/toolkit/query/react";
import { COMMON_API_URL } from "../../../constants/apiUrls";
import { axiosBaseQuery } from "../../../utils/helper";

export const membersApis = createApi({
  baseQuery: axiosBaseQuery({
    baseUrl: ``,
  }),
  reducerPath: "members",
  keepUnusedDataFor: 5,
  refetchOnMountOrArgChange: true,
  endpoints: (builder) => ({
    getMember: builder.query<any, any>({
      query: (args: any) => {
        const { id } = args;
        return {
          method: "get",
          url: `${COMMON_API_URL.getMember}${id}`,
        };
      },
    }),
    getAllMembers: builder.query<any, any>({
      query: () => {
        return {
          method: "get",
          url: `${COMMON_API_URL.getMembers}`,
          // params: params,
        };
      },
    }),
    updateMember: builder.mutation({
      query: ({ data }) => {
        const { id } = data;
        return {
          url: `${COMMON_API_URL.createMember}/${id}`,
          method: "patch",
          data: { ...data.data },
        };
      },
    }),
    createMember: builder.mutation({
      query: ({ data }) => {
        return {
          url: `${COMMON_API_URL.createMember}`,
          method: "post",
          data: { ...data },
        };
      },
    }),
    changeMember: builder.mutation({
      query: (data) => {
        const { id, ...body } = data;
        return {
          url: `${COMMON_API_URL.changeMember}/${id}`,
          method: "PUT",
          data: body,
        };
      },
    }),

    deleteMember: builder.mutation({
      query: (data) => {
        return {
          url: `${COMMON_API_URL.deleteMember}/${data}`,
          method: "delete",
        };
      },
    }),
  }),
});
export const {
  useCreateMemberMutation,
  useGetAllMembersQuery,
  useGetMemberQuery,
  useUpdateMemberMutation,
  useDeleteMemberMutation,
  useChangeMemberMutation,
} = membersApis;
