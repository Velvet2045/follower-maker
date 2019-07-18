///////////////////////////////////////////////////////////////////////////
// 필수 추가 헤더
#include "ProgramInstaller.h"

////////////////////////////////////////////////////////////////////////////
// 파라메터 : 프로세스 이름 (예) "notepad.exe"
// 프로세스가 없거나 종료 성공하면 TRUE, 종료에 실패하면 FALSE
BOOL ProcessAllKill(char* szProcessName)
{
	HANDLE hndl = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
	DWORD dwsma = GetLastError();
	HANDLE hHandle;

	DWORD dwExitCode = 0;

	PROCESSENTRY32  procEntry = { 0 };
	procEntry.dwSize = sizeof(PROCESSENTRY32);
	Process32First(hndl, &procEntry);
	while (1)
	{
		if (!strcmp(procEntry.szExeFile, szProcessName))
		{

			hHandle = ::OpenProcess(PROCESS_ALL_ACCESS, 0, procEntry.th32ProcessID);

			if (::GetExitCodeProcess(hHandle, &dwExitCode))
			{
				if (!::TerminateProcess(hHandle, dwExitCode))
				{
					return FALSE;
				}
			}
		}
		if (!Process32Next(hndl, &procEntry))
		{
			return TRUE;
		}
	}


	return TRUE;
}


////////////////////////////////////////////////////////////////////////////
// 테스트 코드
void main()
{
	std::string strFileName = "chromedriver.exe";
	if (ProcessAllKill((char *)strFileName.c_str()))
		printf("성공\n");
	else
		printf("실패\n");

	return;
}