package testing;

import static junit.framework.Assert.fail;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.lang.reflect.Field;
import java.util.Map;
import java.util.Timer;
import java.util.TimerTask;

public class NS2Simulation {

	private static final int ABORT_TIME = 120 * 1000;
	
	private boolean aborted = false;
	
	public synchronized void setAborted() {
		aborted = true;
	}
	
	public synchronized boolean wasAborted() {
		return aborted;
	}

	public boolean runScript(final String workingDir, final String script, final String outputDir) {
		final String outputFilePath = outputDir + File.separatorChar + "output.log";
		final String errorFilePath = outputDir + File.separatorChar + "error.log";

		boolean finished = false;

		// Execute command
		final ProcessBuilder pb = new ProcessBuilder(getNSExecutablePath(), script);
		final Map<String, String> env = pb.environment();

		if (checkEnvironment(env)) {

			final String NS2_PATH = env.get("NS_DIR");
			final String AGENTJ_PATH = env.get("AGENTJ");
			final String JAVA_HOME = env.get("JAVA_HOME");

			final String NS2_BIN_PATH = NS2_PATH + File.separatorChar + "bin";
			final String NS2_TCL_PATH = NS2_PATH + File.separatorChar + "tcl8.4.18" + File.separatorChar + "unix";
			final String NS2_TCL_LIB_PATH = NS2_PATH + File.separatorChar + "tcl8.4.18" + File.separatorChar + "library";
			final String NS2_TK_PATH = NS2_PATH + File.separatorChar + "tk8.4.18" + File.separatorChar + "unix";
			final String NS2_OTCL_PATH = NS2_PATH + File.separatorChar + "otcl-1.13";
			final String NS2_LIB_PATH = NS2_PATH + File.separatorChar + "lib";

			final String AGENTJ_CORE_LIB = AGENTJ_PATH + File.separator + "core" + File.separator + "lib";
			final String JAVA_AMD64_LIB = JAVA_HOME + File.separator + "jre" + File.separator + "lib" + File.separator + "amd64" + File.separator + "server";

			final String CLASSPATH = AGENTJ_PATH + File.separator + "core" + File.separator + "target" + File.separator + "agentj-core-1.0.jar" + File.pathSeparator + AGENTJ_CORE_LIB + File.separator + "proto-logging-0.1.jar";

			// Set to the current Eclipse classpath
			final String AGENTJ_CLASSPATH = System.getProperty("java.class.path");

			env.put("PATH", env.get("PATH") + File.pathSeparator + NS2_BIN_PATH + File.pathSeparator + NS2_TCL_PATH + File.pathSeparator + NS2_TK_PATH);
			env.put("LD_LIBRARY_PATH", env.get("LD_LIBRARY_PATH") + File.pathSeparator + NS2_OTCL_PATH + File.pathSeparator + NS2_LIB_PATH);
			env.put("TCL_LIBRARY", env.get("TCL_LIBRARY") + File.pathSeparator + NS2_TCL_LIB_PATH);

			env.put("AGENTJ", AGENTJ_PATH);
			env.put("JAVA_HOME", JAVA_HOME);
			env.put("LD_LIBRARY_PATH", env.get("LD_LIBRARY_PATH") + File.pathSeparator + AGENTJ_CORE_LIB + File.pathSeparator + JAVA_AMD64_LIB);
			env.put("AGENTJ_CLASSPATH", AGENTJ_CLASSPATH);
			env.put("CLASSPATH", env.get("CLASSPATH") + File.pathSeparator + CLASSPATH);

			pb.directory(new File(workingDir));
			try {
				final Process p = pb.start();
	
				final ReadProcessOutput readOutput = new ReadProcessOutput(p.getInputStream(), outputFilePath);
				readOutput.start();
	
				final ReadProcessOutput readErrorOutput = new ReadProcessOutput(p.getErrorStream(), errorFilePath);
				readErrorOutput.start();
	
				final Timer timer = new Timer(true);
				try {
					final InterruptTimerTask interrupter = new InterruptTimerTask(p, workingDir + File.pathSeparator + script, this);
					timer.schedule(interrupter, ABORT_TIME);
					finished = (p.waitFor() == 0);
				} catch (final InterruptedException e) {
					System.out.println("NS-2 simulation process was interrupted.");
				} finally {
					timer.cancel();
				}
	
				readOutput.interrupt();
				readOutput.join();
				readErrorOutput.interrupt();
				readErrorOutput.join();
				
			} catch (Exception e) {
				fail("NS-2 process could not be started. " + e.getMessage()); 
			}
			
			try {
				if (wasAborted()) { 
					SaveOutputDirAction saveOutputDirAction = new SaveOutputDirAction(workingDir, "expired");
					saveOutputDirAction.perform();
				}
				else if (!finished) {
					SaveOutputDirAction saveOutputDirAction = new SaveOutputDirAction(workingDir, "notFinished");
					saveOutputDirAction.perform();
				}
			} catch (Exception e) {
				System.out.print(e.getMessage());
			}
			
		} else
			fail("Environment variables were not correctly set. Needed variables: NS_DIR, AGENTJ and JAVA_HOME");
			
		return finished;
	}

	private boolean checkEnvironment(final Map<String, String> env) {
		final String NS2_PATH = env.get("NS_DIR");
		final String AGENTJ_PATH = env.get("AGENTJ");
		final String JAVA_HOME = env.get("JAVA_HOME");

		if (NS2_PATH == null) {
			System.out.println("NS_DIR environment variable not set");
			return false;
		} else if (AGENTJ_PATH == null) {
			System.out.println("AGENTJ environment variable not set");
			return true;
		} else if (JAVA_HOME == null) {
			System.out.println("JAVA_HOME environment variable not set");
			return true;
		}
		return true;
	}

	private String getNSExecutablePath() {
		final ProcessBuilder pb = new ProcessBuilder("");
		final Map<String, String> env = pb.environment();

		final String NS2_PATH = env.get("NS_DIR");

		final String NS2_BIN_PATH = NS2_PATH + File.separatorChar + "bin";
		final String NS2_EXECUTABLE_PATH = NS2_BIN_PATH + File.separatorChar + "ns";

		return NS2_EXECUTABLE_PATH;
	}

	private static class InterruptTimerTask extends TimerTask {

		private final Process process;
		private final String interruptedScript; 
		private final NS2Simulation simulation;

		public InterruptTimerTask(final Process process, final String interruptedScript, final NS2Simulation simulation) {
			this.process = process;
			this.interruptedScript = interruptedScript;
			this.simulation = simulation;
		}

		@Override
		public void run() {
			System.out.println("Interrupting execution of " + interruptedScript);
			simulation.setAborted();
			destroy();
		}
		
		private void destroy() {
			try {
				final int pid = getUnixPID();
				System.out.println("Killing process with PID " + pid);
				Runtime.getRuntime().exec("kill -9 " + pid);
			} catch (Exception e) {
				System.out.println(e.getMessage());
			}
		}

		private int getUnixPID() throws IllegalArgumentException, IllegalAccessException, NoSuchFieldException {  
	        if (process.getClass().getName().equals("java.lang.UNIXProcess")) {  
	            Class<? extends Process> proc = process.getClass();  
	            Field field = proc.getDeclaredField("pid");  
	            field.setAccessible(true);  
	            Object pid = field.get(process);  
	            return (Integer) pid;  
	        } else {  
	            throw new IllegalArgumentException("Not a UNIXProcess");  
	        }  
	    }  
	}

	private static class ReadProcessOutput extends Thread {

		private final String newLineSeparator = System.getProperty("line.separator");

		private final InputStream is;
		private final String filePath;

		public ReadProcessOutput(final InputStream is, final String filePath) {
			this.is = is;
			this.filePath = filePath;
		}

		@Override
		public void run() {
			final BufferedReader br = new BufferedReader(new InputStreamReader(is));
			String line = null;
			BufferedWriter writer = null;

			try {
				writer = new BufferedWriter(new FileWriter(filePath));
				while (!Thread.interrupted() && (line = br.readLine()) != null)
					writer.write(line + newLineSeparator);
			} catch (final IOException e) {
				System.out.print(e.getMessage());
			} finally {
				try {
					br.close();
				} catch (final IOException e) {
					System.out.print(e.getMessage());
				}
				
				try {
					if (writer != null)
						writer.close();
				} catch (final IOException e) {
					System.out.print(e.getMessage());
				}
			}
		}
	}
}
