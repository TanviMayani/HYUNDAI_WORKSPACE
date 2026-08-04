import * as React from "react";
import DashboardIcon from "@mui/icons-material/Dashboard";
import BorderColorOutlinedIcon from "@mui/icons-material/BorderColorOutlined";
import PeopleIcon from "@mui/icons-material/People";
import Item from "../SideBarListItem";
import KeyIcon from "@mui/icons-material/Key";
import GroupIcon from "@mui/icons-material/Group";
import WebhookIcon from "@mui/icons-material/Webhook";
import { useModuleListQuery } from "../../redux/features/commonApis";
import { useState, useEffect } from "react";
import { useLocation } from "react-router-dom";
import StackedBarChartIcon from "@mui/icons-material/StackedBarChart";

interface ModuleInfo {
  module_name: string;
  module_id?: string;
  read?: boolean;
  full_access?: boolean;
}

interface NavigationItem {
  href: string;
  icon: React.ElementType;
  name: string;
  module_name?: string;
  visibility: boolean;
  children?: NavigationItem[];
}

const navigationConfig: NavigationItem[] = [
  {
    href: "/dashboard/tiles",
    icon: DashboardIcon,
    name: "Dashboard",
    visibility: true,
  },
  {
    href: "/dashboard/analytics",
    icon: StackedBarChartIcon,
    name: "Analytics",
    visibility: true,
  },
  {
    href: "/dashboard/jobs",
    icon: BorderColorOutlinedIcon,
    name: "Create Job",
    module_name: "extract",
    visibility: false,
  },
  {
    href: "/dashboard/my-jobs",
    icon: PeopleIcon,
    name: "My Job",
    visibility: false,
  },
  {
    href: "/dashboard/summarize",
    icon: PeopleIcon,
    name: "Summarize",
    module_name: "summarize",
    visibility: false,
  },
  {
    href: "/dashboard/translate",
    icon: PeopleIcon,
    name: "Translate",
    module_name: "translate",
    visibility: false,
  },
  {
    href: "/dashboard/doc-query",
    icon: PeopleIcon,
    name: "Doc Query",
    module_name: "doc_query",
    visibility: false,
  },
  {
    href: "/dashboard/classification",
    icon: PeopleIcon,
    name: "Classification",
    module_name: "classification",
    visibility: false,
  },
  {
    href: "/dashboard/name-entity-recongnition",
    icon: PeopleIcon,
    name: "Name Entity Recongnition",
    module_name: "name_entity_recongnition",
    visibility: false,
  },
  {
    href: "/dashboard/sentiment-analysis",
    icon: PeopleIcon,
    name: "Sentiment Analysis",
    module_name: "sentiment_analysis",
    visibility: false,
  },
];

const settingNavigation: NavigationItem[] = [
  {
    href: "#",
    icon: "",
    name: "",
    visibility: true,
    children: [
      {
        href: "/dashboard/settings/api-key",
        name: "API Key",
        icon: KeyIcon,
        visibility: true,
      },
      {
        href: "/dashboard/settings/webhooks",
        name: "Webhooks",
        icon: WebhookIcon,
        visibility: true,
      },
      {
        href: "/dashboard/settings/groups",
        name: "Groups & Members",
        icon: GroupIcon,
        visibility: true,
      },
      {
        href: "/dashboard/settings/service",
        name: "Service",
        icon: GroupIcon,
        visibility: true,
      },
    ],
  },
];

interface MainListItemsProps {
  isSidebarOpen: boolean;
}

export const MainListItems: React.FC<MainListItemsProps> = ({
  isSidebarOpen,
}) => {
  const url = useLocation();
  const [syncList, setSyncList] = useState<NavigationItem[]>([]);
  const { data } = useModuleListQuery({});
  const isSetting = url.pathname.includes("setting");

  const mergedConfig = navigationConfig.map((navItem) => {
    const moduleInfo = data?.find(
      (module: ModuleInfo) => module.module_name === navItem.module_name
    );
    return {
      ...navItem,
      ...(moduleInfo
        ? {
            module_id: moduleInfo.module_id,
            read: moduleInfo.read,
            full_access: moduleInfo.full_access,
          }
        : {}),
    };
  });

  useEffect(() => {
    setSyncList(isSetting ? settingNavigation : mergedConfig);
  }, [data, isSetting]);

  const updatedNavigationConfig = syncList.map((item) => {
    if (item.href === "#") {
      const updatedChildren =
        item.children?.map((child) => ({
          ...child,
          visibility: child.href === url.pathname,
        })) ?? [];
      return { ...item, children: updatedChildren, visibility: true };
    }
    return item;
  });

  return (
    <React.Fragment>
      {updatedNavigationConfig
        .filter(
          (item) =>
            item.visibility ||
            (item.children && item.children.some((child) => child.visibility))
        )
        .map((item) => (
          <Item key={item.name} item={item} isSidebarOpen={isSidebarOpen} />
        ))}
    </React.Fragment>
  );
};
