/*
*
*   Copyright (c) 2012 Unai Aguilera
*
*   Licensed under the Apache License, Version 2.0 (the "License");
*   you may not use this file except in compliance with the License.
*   You may obtain a copy of the License at
*
*       http://www.apache.org/licenses/LICENSE-2.0
*
*   Unless required by applicable law or agreed to in writing, software
*   distributed under the License is distributed on an "AS IS" BASIS,
*   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
*   See the License for the specific language governing permissions and
*   limitations under the License.
*
*  
*   Author: Unai Aguilera <gkalgan@gmail.com>
*/
package testing;

import java.io.File;

import org.apache.commons.io.FileUtils;

class SaveOutputDirAction implements InterruptionAction {
	
	private final String outputDir;
	private final String cause;
	
	public SaveOutputDirAction(final String outputDir, final String cause) {
		this.outputDir = outputDir;
		this.cause = cause;
	}

	@Override
	public void perform() throws Exception {
		File wDir = new File(outputDir);
		File tempDir = new File(System.getProperty("java.io.tmpdir") + File.separatorChar + wDir.getName() + "-" + cause + "-" + System.currentTimeMillis());
		tempDir.mkdir();
		
		File oDir = new File(outputDir);
		FileUtils.copyDirectory(oDir, tempDir);
	}
	
}
