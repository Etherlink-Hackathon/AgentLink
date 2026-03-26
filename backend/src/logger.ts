import winston from "winston";

const { combine, timestamp, colorize, printf } = winston.format;

const logFormat = printf(({ level, message, timestamp: ts, ...meta }) => {
  const metaStr = Object.keys(meta).length ? ` ${JSON.stringify(meta)}` : "";
  return `${ts} [${level}] ${message}${metaStr}`;
});

export function createLogger(level: string = "info"): winston.Logger {
  return winston.createLogger({
    level,
    format: combine(timestamp({ format: "YYYY-MM-DD HH:mm:ss" }), logFormat),
    transports: [
      new winston.transports.Console({
        format: combine(
          colorize(),
          timestamp({ format: "YYYY-MM-DD HH:mm:ss" }),
          logFormat
        ),
      }),
      new winston.transports.File({
        filename: "agent.log",
        maxsize: 5 * 1024 * 1024, // 5MB
        maxFiles: 3,
      }),
    ],
  });
}

/** Default logger instance — reconfigured at startup by index.ts */
export let logger = createLogger("info");

export function setLogger(newLogger: winston.Logger): void {
  logger = newLogger;
}
