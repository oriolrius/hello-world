# S6 — recover the app after a VM rebuild (recovery checkpoint)

At S6 the workspace VM can be destroyed and rebuilt; your **application** survives
because it was **committed and released**, not because it lived on the VM disk.
Recovery re-releases the last version through your S5 pipeline (unchanged
VM_HOST/VM_SSH_KEY) and redeploys the committed registry compose — see the
ec2-console recovery runbook (RESTORE.md). The app tree does not change at S6;
this checkpoint marks the recovery baseline.
