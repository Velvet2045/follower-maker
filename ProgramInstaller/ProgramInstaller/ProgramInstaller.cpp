///////////////////////////////////////////////////////////////////////////
// �ʼ� �߰� ���
#include "ProgramInstaller.h"

////////////////////////////////////////////////////////////////////////////
// �Ķ���� : ���μ��� �̸� (��) "notepad.exe"
// ���μ����� ���ų� ���� �����ϸ� TRUE, ���ῡ �����ϸ� FALSE
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
// �׽�Ʈ �ڵ�
void main()
{
	std::string strFileName = "chromedriver.exe";
	if (ProcessAllKill((char *)strFileName.c_str()))
		printf("����\n");
	else
		printf("����\n");

	return;
}