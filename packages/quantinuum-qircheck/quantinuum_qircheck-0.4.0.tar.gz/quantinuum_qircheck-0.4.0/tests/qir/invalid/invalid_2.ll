; ModuleID = 'hugr-qir'
source_filename = "hugr-qir"
target datalayout = "e-m:e-i8:8:32-i16:16:32-i64:64-i128:128-n32:64-S128"
target triple = "aarch64-unknown-linux-gnu"

%Qubit = type opaque
%Result = type opaque

@0 = private unnamed_addr constant [2 x i8] c"0\00", align 1
@1 = private unnamed_addr constant [2 x i8] c"1\00", align 1

define void @__hugr__.main.1() local_unnamed_addr #0 {
alloca_block:
  br label %cond_exit_176

cond_104_case_0:                                  ; preds = %cond_exit_176, %4
  %"65_0.0" = phi i64 [ %5, %4 ], [ %"15_0.0221", %cond_exit_176 ]
  %0 = icmp slt i64 %"65_0.0", 10
  br i1 %0, label %cond_exit_176, label %cond_132_case_1

cond_132_case_1:                                  ; preds = %cond_104_case_0
  tail call void @__quantum__qis__mz__body(%Qubit* null, %Result* null)
  %1 = tail call i1 @__quantum__qis__read_result__body(%Result* null)
  tail call void @__quantum__rt__bool_record_output(i1 %1, i8* getelementptr inbounds ([2 x i8], [2 x i8]* @0, i64 0, i64 0))
  tail call void @__quantum__qis__mz__body(%Qubit* nonnull inttoptr (i64 2 to %Qubit*), %Result* nonnull inttoptr (i64 2 to %Result*))
  %2 = tail call i1 @__quantum__qis__read_result__body(%Result* nonnull inttoptr (i64 2 to %Result*))
  tail call void @__quantum__rt__bool_record_output(i1 %2, i8* getelementptr inbounds ([2 x i8], [2 x i8]* @1, i64 0, i64 0))
  ret void

cond_exit_176:                                    ; preds = %alloca_block, %cond_104_case_0
  %"15_0.0221" = phi i64 [ 0, %alloca_block ], [ %"65_0.0", %cond_104_case_0 ]
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 1 to %Qubit*))
  tail call void @__quantum__qis__rz__body(double 0x400921FB54442D18, %Qubit* nonnull inttoptr (i64 1 to %Qubit*))
  tail call void @__quantum__qis__mz__body(%Qubit* nonnull inttoptr (i64 1 to %Qubit*), %Result* nonnull inttoptr (i64 1 to %Result*))
  %3 = tail call i1 @__quantum__qis__read_result__body(%Result* nonnull inttoptr (i64 1 to %Result*))
  br i1 %3, label %4, label %cond_104_case_0

4:                                                ; preds = %cond_exit_176
  %5 = add nsw i64 %"15_0.0221", 1
  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0xBFF921FB54442D18, %Qubit* null)
  tail call void @__quantum__qis__rz__body(double 0x400921FB54442D18, %Qubit* null)
  br label %cond_104_case_0
}

declare void @__quantum__qis__phasedx__body(double, double, %Qubit*) local_unnamed_addr

declare void @__quantum__qis__rz__body(double, %Qubit*) local_unnamed_addr

declare void @__quantum__qis__mz__body(%Qubit*, %Result*) local_unnamed_addr

declare i1 @__quantum__qis__read_result__body(%Result*) local_unnamed_addr

declare void @__quantum__rt__bool_record_output(i1, i8*) local_unnamed_addr

attributes #0 = { "entry_point" "output_labeling_schema" "qir_profiles"="custom" "required_num_qubits"="3" "required_num_results"="3" }

!llvm.module.flags = !{!0, !1, !2, !3}

!0 = !{i32 1, !"qir_major_version", i32 1}
!1 = !{i32 7, !"qir_minor_version", i32 0}
!2 = !{i32 1, !"dynamic_qubit_management", i1 false}
!3 = !{i32 1, !"dynamic_result_management", i1 false}