import { isNotEmptyString } from "../utils/is";

const auth = async (
  req: { header: (arg0: string) => any },
  res: { send: (arg0: { status: string; message: any; data: null }) => void },
  next: () => void
) => {
  var AUTH_SECRET_KEY = "";
  if (process.env.AUTH_SECRET_KEY) {
    AUTH_SECRET_KEY = process.env.AUTH_SECRET_KEY;
  }

  if (isNotEmptyString(AUTH_SECRET_KEY)) {
    try {
      const Authorization = req.header("Authorization");
      if (
        !Authorization ||
        Authorization.replace("Bearer ", "").trim() !== AUTH_SECRET_KEY.trim()
      )
        throw new Error("Error: 无访问权限 | No access rights");
      next();
    } catch (error : any) {
      res.send({
        status: "Unauthorized",
        message: error.message ?? "Please authenticate.",
        data: null,
      });
    }
  } else {
    next();
  }
};

export { auth };
