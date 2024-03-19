import axios from "axios";
import { useQuery } from "react-query";
import { CopyToClipboard } from "react-copy-to-clipboard";
import { jwtDecode } from "jwt-decode";

export const WorkPage: React.FC = () => {
  const axiosClient = axios.create();

  const { isLoading, data, refetch, isError } = useQuery(
    "logged-in-user-info",
    async () => {
      return await axiosClient
        .get("/api/logged-in-user-info")
        .then((r) => r.data);
    },
  );

  const exchange = async (num: number) => {
    await axiosClient.post(`/exchange-broker-${num}`).then(() => {
      refetch();
    });
  };

  const logout = async (num: number) => {
    await axiosClient.post(`/logout-broker-${num}`).then(() => {
      refetch();
    });
  };

  const objectToListItems = (d: any) => {
    return Object.entries(d).map(([k, v]) => {
      // if we are passed down a JSON object all we do is render it
      if (typeof v === "object") {
        return (
          <div className="col">
            <div className="card">
              <div className="card-header">{k}</div>
              <div className="card-body">
                <pre className="small text-monospace">
                  {JSON.stringify(v, null, 2).trimEnd()}
                </pre>
              </div>
            </div>
          </div>
        );
      }

      if (!(typeof v === "string" || v instanceof String))
        throw new Error("Passed data that was neither an object or a string");

      const token = v.toString();

      // a special card for passport scoped access token - we can exchange these
      const re = /Broker (.*?) Passport-Scoped Access Token/;
      const reResult = re.exec(k);

      if (reResult) {
        return (
          <div className="col">
            <div className="card">
              <div className="card-header">
                <button
                  type="button"
                  className="btn btn-success btn-sm"
                  onClick={() => exchange(parseInt(reResult[1]))}
                >
                  Exchange
                </button>
                &nbsp;
                <button
                  type="button"
                  className="btn btn-danger btn-sm"
                  onClick={() => logout(parseInt(reResult[1]))}
                >
                  Logout
                </button>
                &nbsp;
                {k}
              </div>
              <div className="card-body">
                <p className="card-text">{token}</p>
              </div>
            </div>
          </div>
        );
      }

      if (token.startsWith("ey")) {
        const decodedBody = jwtDecode(token) as Record<string, object>;
        const decodedHeader = jwtDecode(token, { header: true }) as Record<
          string,
          object
        >;

        const foundVisasRaw: string[] = [];
        const foundVisasObjects: unknown[] = [];

        if ("ga4gh_passport_v1" in decodedBody) {
          const visaTokenArray = decodedBody["ga4gh_passport_v1"];

          if (Array.isArray(visaTokenArray)) {
            let index = 0;
            for (const visaToken of visaTokenArray) {
              foundVisasRaw.push(visaToken);

              const visaDecodedBody = jwtDecode(visaToken);
              const visaDecodedHeader = jwtDecode(visaToken, { header: true });

              foundVisasObjects.push(` ---- decoded visa [${index++}] ---- `);
              foundVisasObjects.push(visaDecodedHeader);
              foundVisasObjects.push(visaDecodedBody);
            }
          }
        }

        if (foundVisasObjects.length > 0) {
          decodedBody["ga4gh_passport_v1"] = foundVisasObjects;
        }

        return (
          <div className="col">
            <div className="card">
              <div className="card-header">
                { foundVisasObjects.length > 0 && <>
                <CopyToClipboard text={token}>
                  <button type="button" className="btn btn-warning btn-sm">
                    Copy Passport
                  </button>
                </CopyToClipboard>
                &nbsp;
                </>}
                {k}
              </div>
              <div className="card-body">
                <pre style={{ fontSize: "10px" }} className="text-monospace">
                  {JSON.stringify(decodedHeader, null, 2).trimEnd()}
                </pre>
                <pre style={{ fontSize: "10px" }} className="text-monospace">
                  {JSON.stringify(decodedBody, null, 2).trimEnd()}
                </pre>
              </div>
              {foundVisasRaw.length > 0 && (
                  <div className="card-footer">
                    {foundVisasRaw.map((raw, index) => (
                        <>
                        <CopyToClipboard key={index} text={raw}>
                            <button
                                type="button"
                                className="btn btn-primary btn-sm"
                            >
                              Copy Visa {index}
                            </button>
                        </CopyToClipboard>
                          &nbsp;
                        </>
                    ))}
                    <button type="button" disabled={true} className="btn btn-danger btn-sm">Send to htsget</button>
                    &nbsp;
                    <button type="button" disabled={true} className="btn btn-danger btn-sm">Send to drs</button>
                  </div>
              )}
            </div>
          </div>
        );
      }

      return (
          <div className="col">
          <div className="card">
            <div className="card-header">{k}</div>
            <div className="card-body">
              <p className="card-text">{token}</p>
            </div>
          </div>
        </div>
      );
    });
  };

  return (
    <>
      <div className="hstack gap-4 mb-4">
        <form action="/login-broker-1" method="POST" id="broker1TriggerForm">
          <button className="btn btn-outline-primary" type="submit">
            Login Broker 1
          </button>
        </form>
        <form action="/login-broker-2" method="POST" id="broker2TriggerForm">
          <button className="btn btn-outline-primary" type="submit">
            Login Broker 2
          </button>
        </form>
        <form action="/login-broker-3" method="POST" id="broker2TriggerForm">
          <button className="btn btn-outline-primary" type="submit">
            Login Broker 3
          </button>
        </form>
        <span>{isError.toString()}</span>
      </div>
      {isLoading && <span>Loading</span>}
      {data && (
          <>
            <p>
              The following data is known by the server about the currently logged
              in user. All of this data is securely maintained via cookies in an
              "session" state - and is not visible to the front-end. In order
              for the front-end to see this information we
              have explicitly added an extra API to show all the details below (which obviously
              would not be something done in a production system).
            </p>
            <p>
              &nbsp;
            </p>
            <div className="row row-cols-1 row-cols-md-2 g-4">
              {objectToListItems(data)}
            </div>
            <p>
              &nbsp;
            </p>
          </>
      )}
    </>
  );
};
