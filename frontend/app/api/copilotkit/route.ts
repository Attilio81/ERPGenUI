import {
  CopilotRuntime,
  ExperimentalEmptyAdapter,
  copilotRuntimeNextJSAppRouterEndpoint,
} from "@copilotkit/runtime";
import { AgnoAgent } from "@ag-ui/agno";
import { NextRequest } from "next/server";

const serviceAdapter = new ExperimentalEmptyAdapter();

const AGENT_URL = (process.env.AGENT_URL || "http://localhost:7000").replace(/\/$/, "");

const runtime = new CopilotRuntime({
  agents: {
    // il nome 'my_agent' deve combaciare con useCoAgent({name}) e <CopilotKit agent>
    my_agent: new AgnoAgent({ url: `${AGENT_URL}/agui` }),
  },
});

export const POST = async (req: NextRequest) => {
  const { handleRequest } = copilotRuntimeNextJSAppRouterEndpoint({
    runtime,
    serviceAdapter,
    endpoint: "/api/copilotkit",
  });
  return handleRequest(req);
};
